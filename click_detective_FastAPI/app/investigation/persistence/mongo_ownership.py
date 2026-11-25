"""계정의 수사 목록을 조회하고 익명 수사를 계정에 연결한다."""

from base64 import urlsafe_b64decode, urlsafe_b64encode
from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from mongoengine.queryset import Q

from .access import allows_access
from .mongo_odm import preserve_driver_error


def summary(game):
    """수사 문서에서 소유자 목록에 표시할 필드만 읽는다.

    Args:
        game: 수사 식별자와 최근 상태가 있는 MongoDB 문서.

    Returns:
        dict: 수사 ID, 사건, 버전, 갱신 시각과 진행 요약.
    """
    state = game.state
    return {
        "game_id": game.id,
        "case_id": game.case_id,
        "scenario_version": game.scenario_version,
        "revision": game.revision,
        "updated_at": game.updated_at.isoformat(),
        "progress": {
            "phase": state.get("phase", 1),
            "completed": bool(state.get("verdict")),
        },
    }


def cursor_filter(cursor):
    """목록 커서를 MongoDB의 복합 정렬 범위로 변환한다.

    Args:
        cursor: 직전 페이지 마지막 문서의 시각과 UUID를 담은 문자열.

    Returns:
        Q: 다음 페이지의 범위를 표현하는 ODM 조회 조건.
    """
    try:
        raw = urlsafe_b64decode(cursor.encode("ascii")).decode("ascii")
        stamp, game_id = raw.split("|")
        updated_at = datetime.fromisoformat(stamp)
        if updated_at.tzinfo is None or str(UUID(game_id)) != game_id:
            raise ValueError("커서 형식 오류")
    except (ValueError, OverflowError) as error:
        raise HTTPException(400, "수사 목록 커서가 올바르지 않습니다.") from error
    return Q(updated_at__lt=updated_at) | Q(updated_at=updated_at, id__lt=game_id)


def list_owned(storage, user_id, cursor, limit):
    """계정 소유 수사를 가장 최근 갱신 순으로 읽는다.

    Args:
        storage: MongoDB 수사 컬렉션에 접근할 저장소.
        user_id: 인증을 통과한 사용자 UUID.
        cursor: 이전 페이지가 반환한 커서 또는 None.
        limit: 반환할 문서 수로 1~100만 허용한다.

    Returns:
        dict: 현재 페이지의 공개 수사 요약과 다음 커서.
    """
    if not 1 <= limit <= 100:
        raise HTTPException(400, "수사 목록 조회 개수가 올바르지 않습니다.")
    query = storage.games.query(owner_user_id=user_id)
    if cursor is not None:
        query = query.filter(cursor_filter(cursor))
    rows = list(
        query.only(
            "case_id",
            "scenario_version",
            "revision",
            "updated_at",
            "state.phase",
            "state.verdict",
        )
        .order_by("-updated_at", "-id")
        .limit(limit + 1)
    )
    next_cursor = None
    if len(rows) > limit:
        last = rows[limit - 1]
        raw = f"{last.updated_at.isoformat()}|{last.id}"
        next_cursor = urlsafe_b64encode(raw.encode("ascii")).decode("ascii")
    return {"items": [summary(row) for row in rows[:limit]], "next_cursor": next_cursor}


def claim(storage, game_id, token, user_id):
    """익명 수사에 계정 소유권을 부여하고 이전 토큰을 폐기한다.

    Args:
        storage: MongoDB 수사 컬렉션에 접근할 저장소.
        game_id: 연결할 수사 UUID.
        token: 기존 브라우저가 가진 익명 수사 토큰.
        user_id: 연결을 요청한 인증 계정 UUID.

    Returns:
        dict: 연결한 수사의 공개 목록 요약.
    """

    def apply(session):
        """이전 요청의 성공을 복구하거나 익명 수사 소유권을 바꾼다.

        Args:
            session: 수사와 요청 기록을 변경할 트랜잭션 세션.

        Returns:
            InvestigationDocument: 새 소유권을 저장한 수사 문서.
        """
        storage.guard_owner_write(user_id, session)
        game = storage.games.query(session, id=game_id).first()
        if game is None:
            raise HTTPException(404, "수사를 찾을 수 없습니다.")
        if game.owner_user_id == user_id:
            return game
        if not allows_access(game.owner_user_id, game.anonymous_token_hash, token):
            raise HTTPException(404, "수사를 찾을 수 없습니다.")
        storage.operations.query(
            session, game_id=game_id, response__game_token__type="string"
        ).update(unset__response__game_token=1)
        return storage.games.query(session, id=game_id, owner_user_id=None).modify(
            new=True,
            set__owner_user_id=user_id,
            set__anonymous_token_hash=None,
            inc__ownership_version=1,
        )

    return summary(storage.transaction(apply))


def delete_owned(storage, user_id):
    """탈퇴 대기 계정의 모든 수사와 연결된 요청을 삭제한다.

    Args:
        storage: MongoDB 수사 컬렉션에 접근할 저장소.
        user_id: 지울 계정의 UUID. 작업 전에 계정과 세션을 차단한다.

    Returns:
        None: 계정에 남은 수사가 없음을 확인한다.
    """

    def remove_game(game_id, session):
        """같은 수사의 상태와 요청 문서를 원자적으로 삭제한다.

        Args:
            game_id: 삭제 대상인지 확인할 수사의 UUID.
            session: MongoDB 트랜잭션 세션.

        Returns:
            None: 현재 계정 소유 수사의 문서만 제거한다.
        """
        deleted = storage.games.query(
            session, id=game_id, owner_user_id=user_id
        ).delete()
        if deleted:
            storage.operations.query(session, game_id=game_id).delete()

    storage.block_owner_writes(user_id)
    with preserve_driver_error():
        query = storage.games.query(owner_user_id=user_id)
        for game_id in query.scalar("id").no_cache():
            storage.transaction(lambda session: remove_game(game_id, session))
        if query.only("id").first() is not None:
            raise RuntimeError("삭제 대기 계정에 수사 기록이 남아 있습니다.")
