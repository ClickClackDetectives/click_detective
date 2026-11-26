"""수사 상태와 재시도 기록을 MongoDB 트랜잭션으로 관리한다."""

import secrets
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException

from app.investigation.repositories import (
    investigation_mongo_ownership as mongo_ownership,
)
from app.investigation.repositories import (
    investigation_mongo_transitions as mongo_transitions,
)
from app.investigation.repositories.investigation_access import (
    AccountAccess,
    token_hash,
)
from app.investigation.repositories.investigation_mongo_documents import (
    InvestigationDocument,
    OperationDocument,
)
from app.investigation.repositories.investigation_mongo_odm import preserve_driver_error
from app.investigation.repositories.investigation_mongo_storage import MongoStorage
from app.investigation.repositories.investigation_storage import digest


class MongoRepository(MongoStorage):
    """익명·계정 수사에 대한 생성, 조회, 변경과 재시도를 지원한다.

    Args:
        uri: MongoDB replica set의 접속 문자열.
        database: 수사와 요청 기록을 보관할 데이터베이스 이름.

    Returns:
        MongoRepository: GameService에 전달할 MongoDB 저장소.
    """

    def get(self, game_id, token):
        """현재 권한으로 저장된 수사를 읽는다.

        Args:
            game_id: 조회할 수사의 UUID.
            token: 익명 수사 토큰 또는 서버가 검증한 계정 문맥.

        Returns:
            dict: 수사의 내부 상태.
        """
        game = self.authorized_game(game_id, token)
        return game.to_mongo()["state"]

    def create(self, request, factory, present, owner=None):
        """새 수사와 같은 요청의 재시도 응답을 함께 저장한다.

        Args:
            request: 사건 ID, 사건 버전과 요청 UUID를 담은 생성 입력.
            factory: 새 수사 UUID로 초기 상태를 생성하는 함수.
            present: 내부 상태를 공개 상태로 바꾸는 함수.
            owner: 새 수사 소유자 UUID 또는 계정 문맥. 익명 시작은 None.

        Returns:
            dict: 수사 ID, 익명 토큰 또는 null, 공개 상태.
        """
        owner_id = owner.user_id if isinstance(owner, AccountAccess) else owner
        key = str(request.request_id)
        body_hash = digest(
            {"action": "create", "body": request.model_dump(mode="json")}
        )

        def apply(session):
            """같은 요청의 결과를 검증하거나 새 수사를 초기화한다.

            Args:
                session: 현재 MongoDB 트랜잭션 세션.

            Returns:
                dict: 수사 ID, 익명 토큰 또는 null, 공개 상태.
            """
            if owner_id is not None:
                self.guard_owner_write(owner_id, session)
            previous = self.operations.query(session, id=key).first()
            if previous is not None:
                if previous.creation_owner_user_id != owner_id:
                    raise HTTPException(404, "수사를 찾을 수 없습니다.")
                if previous.digest != body_hash:
                    raise HTTPException(409, "같은 요청 UUID의 내용이 다릅니다.")
                token = previous.response.get("game_token")
                access = AccountAccess(owner_id) if owner_id is not None else token
                if access is None:
                    raise HTTPException(404, "수사를 찾을 수 없습니다.")
                self.authorized_game(previous.game_id, access, session)
                return previous.to_mongo()["response"]
            now = datetime.now(UTC)
            game_id = str(uuid4())
            token = secrets.token_urlsafe(32) if owner_id is None else None
            state = factory(game_id)
            response = {
                "game_id": game_id,
                "game_token": token,
                "state": present(state),
            }
            game = InvestigationDocument(
                id=game_id,
                owner_user_id=owner_id,
                anonymous_token_hash=token_hash(token) if token is not None else None,
                case_id=request.case_id,
                scenario_version=request.scenario_version,
                schema_version=1,
                ownership_version=0,
                revision=state["revision"],
                state=state,
                updated_at=now,
            )
            operation = OperationDocument(
                id=key,
                game_id=game_id,
                digest=body_hash,
                status="complete",
                response=response,
                completed_at=now,
                creation_owner_user_id=owner_id,
            )
            self.games.insert(game, session)
            self.operations.insert(operation, session)
            return response

        return self.transaction(apply)

    def reserve(self, game_id, token, command, action, lease_seconds, prepare=None):
        """수사 행동을 실행할 예약권을 얻거나 완료 응답을 읽는다.

        Args:
            game_id: 변경할 수사의 UUID.
            token: 익명 수사 토큰 또는 검증된 계정 문맥.
            command: 요청 UUID와 변경 조건 및 입력값.
            action: 실행할 수사 행동의 이름.
            lease_seconds: 예약을 유지할 초 단위 시간.
            prepare: 심문 입력을 검증하는 함수. 제공되면 질문을 함께 차감한다.

        Returns:
            dict: 예약 문맥 또는 저장된 동일 요청의 결과.
        """
        reservation = mongo_transitions.reserve(
            self, game_id, token, command, action, lease_seconds, prepare
        )
        error = reservation.get("cached", {}).get("error")
        if error is not None:
            raise HTTPException(**error)
        return reservation

    def commit(self, game_id, command, reservation, state, result, present):
        """수사 변경과 행동 결과를 같은 트랜잭션에서 확정한다.

        Args:
            game_id: 변경할 수사의 UUID.
            command: 실행권을 예약한 요청.
            reservation: 예약 nonce, 기준 revision, 소유권 버전.
            state: 행동 처리 후 수사 상태.
            result: 공개할 행동 결과.
            present: 내부 상태를 공개 응답으로 바꾸는 함수.

        Returns:
            dict: 요청 ID, 행동 결과와 공개 상태.
        """
        return mongo_transitions.commit(
            self, game_id, command, reservation, state, result, present
        )

    def abort(self, command, reservation, failure=None):
        """실패한 예약을 해제하거나 이미 차감한 심문의 오류를 저장한다.

        Args:
            command: 실패한 수사 행동의 입력과 요청 UUID.
            reservation: 실패한 실행의 예약 nonce.
            failure: 예약을 종료하게 한 예외 또는 None.

        Returns:
            None: 해당 nonce의 pending 상태만 갱신한다.
        """
        updates = {"set__status": "failed"}
        if reservation.get("prepared") is not None and isinstance(
            failure, HTTPException
        ):
            error = {
                "status_code": failure.status_code,
                "detail": failure.detail,
                "headers": failure.headers,
            }
            updates = {
                "set__status": "complete",
                "set__response": {"error": error},
                "set__completed_at": datetime.now(UTC),
            }
        with preserve_driver_error():
            self.operations.query(
                id=str(command.request_id), nonce=reservation["nonce"], status="pending"
            ).update_one(**updates)

    def claim(self, game_id, token, user_id):
        """익명 수사를 인증한 계정 소유로 전환한다.

        Args:
            game_id: 연결할 수사의 UUID.
            token: 익명 수사 토큰.
            user_id: 검증된 계정 UUID.

        Returns:
            dict: 연결된 수사의 공개 요약.
        """
        return mongo_ownership.claim(self, game_id, token, user_id)

    def list_owned(self, user_id, cursor=None, limit=20):
        """로그인 계정이 소유한 수사를 최근 갱신 순으로 조회한다.

        Args:
            user_id: 검증된 계정 UUID.
            cursor: 이전 페이지에서 받은 목록 커서 또는 None.
            limit: 한 페이지에 표시할 최대 수사 개수.

        Returns:
            dict: 계정 수사 요약 목록과 다음 페이지 커서.
        """
        return mongo_ownership.list_owned(self, user_id, cursor, limit)

    def delete_owned(self, user_id):
        """탈퇴 대기 계정의 수사와 그 요청 기록을 제거한다.

        Args:
            user_id: 신규 활동과 세션을 먼저 차단한 삭제 대상 계정 UUID.

        Returns:
            None: 계정 수사와 해당 요청 기록의 삭제를 끝낸다.
        """
        mongo_ownership.delete_owned(self, user_id)
