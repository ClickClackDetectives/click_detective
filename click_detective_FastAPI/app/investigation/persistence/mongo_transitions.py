"""MongoDB에 수사 행동 예약과 완료 결과를 확정한다."""

from copy import deepcopy
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException

from .storage import digest


def reserve(storage, game_id, token, command, action, lease_seconds, prepare=None):
    """수사 행동을 예약하거나 이미 확정한 결과를 읽는다.

    Args:
        storage: MongoDB 수사와 요청 컬렉션을 연결하는 저장소.
        game_id: 수사 UUID.
        token: 익명 접근 토큰 또는 검증된 계정 문맥.
        command: 요청 UUID, 기준 revision, 행동 입력.
        action: 실행할 수사 행동의 이름.
        lease_seconds: 예약 임대 기간(초).
        prepare: 유효한 심문을 준비하는 함수. 제공되면 예약과 함께 질문을 차감한다.

    Returns:
        dict: 실행용 예약 또는 동일 요청의 완료 응답.
    """
    key = str(command.request_id)
    body_hash = digest(
        {"game_id": game_id, "action": action, "body": command.model_dump(mode="json")}
    )

    def apply(session):
        """현재 접근 권한으로 요청 UUID의 실행권을 확보한다.

        Args:
            session: 현재 MongoDB 트랜잭션 세션.

        Returns:
            dict: 예약 문맥 또는 캐시한 응답.
        """
        game = storage.authorized_game(game_id, token, session)
        operation = storage.operations.query(session, id=key).first()
        ownership_version = game.ownership_version
        now = datetime.now(UTC)
        if operation is not None:
            if operation.digest != body_hash:
                raise HTTPException(409, "같은 요청 UUID의 내용이 다릅니다.")
            if operation.status == "complete":
                return {"cached": operation.to_mongo()["response"]}
            if (
                operation.status == "pending"
                and (operation.ownership_version or 0) == ownership_version
                and operation.lease_until > now
            ):
                raise HTTPException(409, "operation_in_progress")
        if game.revision != command.expected_revision:
            raise HTTPException(409, "state_revision_conflict")
        state = game.to_mongo()["state"]
        prepared = prepare(state, command) if prepare else None
        revision = game.revision
        updates = {"inc__reservation_sequence": 1}
        if prepare:
            revision += 1
            state["questions"] += 1
            state["revision"] = revision
            updates.update(
                set__state=state, set__revision=revision, set__updated_at=now
            )
        # 소유권 이전이나 계정 삭제와 예약 작업을 같은 수사 문서에서 직렬화한다.
        storage.games.query(
            session,
            id=game_id,
            revision=game.revision,
            ownership_version=ownership_version,
        ).update_one(**updates)
        nonce = str(uuid4())
        storage.operations.query(session, id=key).update_one(
            upsert=True,
            set__game_id=game_id,
            set__digest=body_hash,
            set__status="pending",
            set__nonce=nonce,
            set__lease_until=now + timedelta(seconds=lease_seconds),
            set__response=None,
            set__completed_at=None,
            set__creation_owner_user_id=None,
            set__ownership_version=ownership_version,
        )
        return {
            "state": state,
            "prepared": prepared,
            "nonce": nonce,
            "revision": revision,
            "ownership_version": ownership_version,
        }

    return storage.transaction(apply)


def commit(storage, game_id, command, reservation, state, result, present):
    """수사 상태와 요청의 완료 응답을 함께 확정한다.

    Args:
        storage: MongoDB 수사와 요청 컬렉션을 연결하는 저장소.
        game_id: 수사 UUID.
        command: 앞서 예약한 수사 행동 입력.
        reservation: 예약 nonce와 기준 revision 및 소유권 버전.
        state: 행동 처리 뒤의 내부 수사 상태.
        result: 행동 처리 결과.
        present: 내부 상태를 공개 화면 상태로 변환하는 함수.

    Returns:
        dict: 요청 UUID와 행동 결과, 확정한 공개 상태.
    """
    key = str(command.request_id)
    operation_filter = {
        "id": key,
        "game_id": game_id,
        "nonce": reservation["nonce"],
        "status": "pending",
    }

    def apply(session):
        """예약권과 수사 버전을 검사해 두 문서를 원자적으로 변경한다.

        Args:
            session: 현재 MongoDB 트랜잭션 세션.

        Returns:
            dict: 확정한 수사와 행동 결과.
        """
        operation = storage.operations.query(session, **operation_filter).first()
        if operation is None:
            raise HTTPException(409, "operation_reservation_conflict")
        game = storage.games.query(session, id=game_id).first()
        if game is None or game.ownership_version != reservation["ownership_version"]:
            raise HTTPException(409, "ownership_changed")
        if game.revision != reservation["revision"]:
            raise HTTPException(409, "state_changed_during_generation")
        now = datetime.now(UTC)
        updated_state = deepcopy(state)
        if updated_state != game.state:
            updated_state["revision"] = game.revision + 1
        storage.games.query(
            session,
            id=game_id,
            revision=reservation["revision"],
            ownership_version=reservation["ownership_version"],
        ).update_one(
            set__revision=updated_state["revision"],
            set__state=updated_state,
            set__updated_at=now,
            inc__commit_sequence=1,
        )
        response = {
            "request_id": key,
            "result": result,
            "state": present(updated_state),
        }
        storage.operations.query(session, **operation_filter).update_one(
            set__status="complete", set__response=response, set__completed_at=now
        )
        return response

    return storage.transaction(apply)
