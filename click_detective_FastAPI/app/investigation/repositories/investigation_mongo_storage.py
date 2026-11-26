"""MongoDB 수사 컬렉션, 인덱스와 트랜잭션을 관리한다."""

from fastapi import HTTPException
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from app.investigation.repositories.investigation_access import allows_access
from app.investigation.repositories.investigation_mongo_documents import (
    InvestigationDocument,
    OperationDocument,
    OwnerDocument,
)
from app.investigation.repositories.investigation_mongo_odm import (
    MappedCollection,
    preserve_driver_error,
)
from app.investigation.repositories.investigation_mongo_schema import (
    prepare_collections,
)


class MongoStorage:
    """수사 저장에 사용할 MongoDB 연결과 트랜잭션을 제공한다.

    Args:
        uri: replica set 또는 샤드 클러스터의 접속 문자열.
        database: 수사 컬렉션을 보관할 데이터베이스 이름.

    Returns:
        MongoStorage: 수사 저장소의 연결과 공통 읽기 경계.
    """

    def __init__(self, uri, database):
        """MongoDB의 트랜잭션 지원을 확인하고 수사 인덱스를 준비한다.

        Args:
            uri: replica set 또는 샤드 클러스터의 접속 문자열.
            database: 수사 컬렉션을 보관할 데이터베이스 이름.

        Returns:
            None: 초기 연결 및 인덱스 준비를 끝낸다.
        """
        self.client = MongoClient(
            uri, tz_aware=True, serverSelectionTimeoutMS=5000, timeoutMS=10000
        )
        try:
            hello = self.client.admin.command("hello")
            if not hello.get("setName") and hello.get("msg") != "isdbgrid":
                raise RuntimeError("MongoDB 수사 저장소에는 replica set이 필요합니다.")
            self.database = self.client.get_database(
                database,
                read_concern=ReadConcern("majority"),
                write_concern=WriteConcern("majority"),
            )
            prepare_collections(self.database)
            self.owners = MappedCollection(
                OwnerDocument, self.database.investigation_owners
            )
            self.games = MappedCollection(
                InvestigationDocument, self.database.investigations
            )
            self.operations = MappedCollection(
                OperationDocument, self.database.investigation_operations
            )
            self.games.collection.create_index(
                [("owner_user_id", 1), ("updated_at", -1), ("_id", -1)]
            )
            self.operations.collection.create_index("game_id")
        except BaseException:
            self.client.close()
            raise

    def close(self):
        """MongoDB 클라이언트와 연결 풀을 닫는다.

        Args:
            없음.

        Returns:
            None: 반환값 없음.
        """
        self.client.close()

    def transaction(self, apply):
        """수사와 요청 문서의 변경을 하나의 트랜잭션에서 확정한다.

        Args:
            apply: 세션을 받아 DB 작업만 수행하는 재시도 가능한 콜백.

        Returns:
            object: 성공한 콜백의 반환값.
        """

        def mapped_apply(session):
            """MongoEngine이 감싼 오류를 복구해 드라이버의 재시도에 전달한다.

            Args:
                session: 현재 PyMongo 트랜잭션 세션.

            Returns:
                object: ODM 콜백의 반환값.
            """
            with preserve_driver_error():
                return apply(session)

        with self.client.start_session() as session:
            try:
                return session.with_transaction(
                    mapped_apply,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority"),
                )
            except DuplicateKeyError:
                # 같은 요청 UUID로 처음 쓰는 트랜잭션이 경합할 수 있다.
                return session.with_transaction(
                    mapped_apply,
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority"),
                )

    def authorized_game(self, game_id, access, session=None):
        """요청 문맥으로 접근할 수 있는 수사 문서를 조회한다.

        Args:
            game_id: 조회할 수사의 문자열 UUID.
            access: 익명 수사 토큰 또는 검증한 계정 문맥.
            session: 조회를 포함하는 트랜잭션 세션. 일반 읽기는 None.

        Returns:
            InvestigationDocument: 접근 가능함을 확인한 수사 문서.
        """
        game = self.games.query(session, id=game_id).first()
        if game is None or not allows_access(
            game.owner_user_id, game.anonymous_token_hash, access
        ):
            raise HTTPException(404, "수사를 찾을 수 없습니다.")
        return game

    def guard_owner_write(self, user_id, session):
        """수사 생성·연결 트랜잭션을 계정의 탈퇴 차단과 직렬화한다.

        Args:
            user_id: PostgreSQL 인증 계정의 UUID.
            session: 수사와 함께 확정할 MongoDB 트랜잭션 세션.

        Returns:
            None: 탈퇴로 영구 차단된 계정이면 세션 오류를 낸다.
        """
        owner = self.owners.query(session, id=user_id).modify(
            upsert=True, new=True, set_on_insert__blocked=False, inc__sequence=1
        )
        if owner.blocked:
            raise HTTPException(
                401, {"code": "SESSION_REVOKED", "message": "다시 로그인하세요."}
            )

    def block_owner_writes(self, user_id):
        """탈퇴를 시작하면서 이후의 수사 생성·연결을 차단한다.

        Args:
            user_id: 모든 세션이 폐기된 탈퇴 계정 UUID.

        Returns:
            None: 지연된 요청을 막을 차단 기록을 유지한다.
        """
        with preserve_driver_error():
            self.owners.query(id=user_id).update_one(
                upsert=True, set__blocked=True, set_on_insert__sequence=0
            )
