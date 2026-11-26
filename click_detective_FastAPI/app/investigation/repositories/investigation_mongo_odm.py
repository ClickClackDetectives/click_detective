"""MongoEngine 쿼리를 기존 MongoDB 트랜잭션 세션에 연결한다."""

from contextlib import contextmanager

from mongoengine import OperationError
from mongoengine.queryset import QuerySet
from pymongo.errors import PyMongoError

SESSION_OPERATIONS = {
    "count_documents",
    "delete_many",
    "find",
    "find_one_and_delete",
    "find_one_and_update",
    "insert_many",
    "insert_one",
    "update_many",
    "update_one",
}


class SessionCollection:
    """MongoEngine 0.29 쿼리에 동일한 PyMongo 세션을 적용한다.

    Args:
        collection: ODM 모델의 기존 BSON 컬렉션.
        session: 한 트랜잭션에서 사용할 PyMongo 세션.

    Returns:
        SessionCollection: 트랜잭션 세션을 보유하는 컬렉션 어댑터.
    """

    def __init__(self, collection, session):
        """컬렉션과 세션을 묶는다.

        Args:
            collection: PyMongo 컬렉션.
            session: 현재 트랜잭션 세션.

        Returns:
            None: 반환값 없음.
        """
        self.collection = collection
        self.session = session

    def with_options(self, **options):
        """저장 옵션을 적용한 컬렉션에도 동일한 세션을 전달한다.

        Args:
            options: MongoEngine이 설정하는 읽기·쓰기 보장 옵션.

        Returns:
            SessionCollection: 갱신한 옵션과 기존 세션을 보관하는 어댑터.
        """
        return SessionCollection(self.collection.with_options(**options), self.session)

    def __getattr__(self, name):
        """MongoEngine이 호출하는 컬렉션 기능에 세션을 전달한다.

        Args:
            name: ODM이 읽을 속성 또는 호출할 PyMongo 메서드 이름.

        Returns:
            object: 메타데이터 또는 트랜잭션 세션이 설정된 호출 함수.
        """
        from functools import partial

        method = getattr(self.collection, name)
        if name in SESSION_OPERATIONS:
            return partial(method, session=self.session)
        return method


@contextmanager
def preserve_driver_error():
    """ODM이 감싼 저장 오류를 기존 트랜잭션 재시도 계층에 전달한다.

    Args:
        없음.

    Returns:
        ContextManager: MongoEngine 오류에서 드라이버 오류를 복구하는 문맥.
    """
    try:
        yield
    except OperationError as error:
        cause = error.__cause__ or error.__context__
        if isinstance(cause, PyMongoError):
            raise cause from None
        raise


class MappedCollection:
    """저장소마다 독립적인 컬렉션을 문서 모델에 연결한다.

    Args:
        model: MongoEngine 문서 모델.
        collection: 해당 저장소가 소유한 PyMongo 컬렉션.

    Returns:
        MappedCollection: 저장소 조회 및 이관에 사용할 문서 매핑.
    """

    def __init__(self, model, collection):
        """문서 모델과 컬렉션의 연결을 설정한다.

        Args:
            model: MongoEngine 문서 모델.
            collection: 데이터베이스별 컬렉션.

        Returns:
            None: 반환값 없음.
        """
        self.model = model
        self.collection = collection

    def query(self, session=None, **filters):
        """문서 필드 이름으로 MongoEngine 쿼리를 구성한다.

        Args:
            session: 조회 또는 변경이 포함될 트랜잭션. 일반 조회에서는 None.
            filters: ODM 문서 필드 기반의 조회 조건.

        Returns:
            QuerySet: 요청 단위로 생성한 MongoEngine 쿼리.
        """
        collection = self.collection
        if session is not None:
            collection = SessionCollection(collection, session)
        return QuerySet(self.model, collection)(**filters)

    def insert(self, document, session):
        """검증한 ODM 문서를 현재 트랜잭션에 삽입한다.

        Args:
            document: 해당 컬렉션의 MongoEngine 문서.
            session: 수사와 요청 기록을 함께 확정할 트랜잭션 세션.

        Returns:
            None: 해당 문서의 삽입 작업을 완료한다.
        """
        document.validate()
        self.query(session).insert(document, load_bulk=False)
