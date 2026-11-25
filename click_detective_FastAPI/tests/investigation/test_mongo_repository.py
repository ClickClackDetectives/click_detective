"""MongoDB 수사 권한과 재시도 계약을 검사한다."""

import os
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import BaseModel

from app.investigation.persistence.access import (
    AccountAccess,
    allows_access,
    token_hash,
)


class Command(BaseModel):
    """저장 계약 검사에 필요한 요청 명령을 나타낸다.

    Args:
        request_id: 요청 UUID 문자열.
        expected_revision: 요청이 기준으로 삼는 상태 버전.

    Returns:
        Command: 테스트용 요청 명령.
    """

    request_id: str
    expected_revision: int = 0
    case_id: str = "fixture"
    scenario_version: str = "v1"


def test_claimed_game_rejects_previous_anonymous_token():
    """소유권이 있는 수사는 예전 익명 토큰으로 열리지 않는다.

    Args:
        없음.

    Returns:
        None: 접근 권한 판정이 다르면 실패한다.
    """
    old_hash = token_hash("old")
    assert not allows_access("owner", old_hash, "old")
    assert not allows_access("owner", old_hash, AccountAccess("other"))
    assert allows_access("owner", old_hash, AccountAccess("owner"))


@pytest.fixture
def mongo_repository():
    """실제 MongoDB 통합 검사에 격리된 컬렉션을 준비한다.

    Args:
        없음.

    Returns:
        Iterator[MongoRepository]: 테스트 후 컬렉션을 정리하는 저장소.
    """
    uri = os.environ.get("CLICK_TEST_MONGO_URI")
    if not uri:
        pytest.skip("CLICK_TEST_MONGO_URI가 필요합니다.")
    from app.investigation.persistence.mongo_repository import MongoRepository

    repo = MongoRepository(uri, f"click_test_{uuid4().hex}")
    try:
        yield repo
    finally:
        try:
            repo.database.investigations.drop()
            repo.database.investigation_operations.drop()
            repo.database.investigation_owners.drop()
        finally:
            repo.close()


def initial_state(game_id):
    """저장 검사용 수사 초기 상태를 만든다.

    Args:
        game_id: 새로 만든 수사 UUID.

    Returns:
        dict: 변경을 시작하기 전의 상태.
    """
    return {"game_id": game_id, "phase": 1, "revision": 0, "examined": []}


def test_claim_blocks_in_flight_commit_and_supports_retry(mongo_repository):
    """계정 연결 뒤 익명 예약은 확정할 수 없고 계정으로 재시도할 수 있다.

    Args:
        mongo_repository: 테스트용 MongoDB 저장소.

    Returns:
        None: 실제 MongoDB에 저장된 예약과 응답을 확인한다.
    """
    repo = mongo_repository
    creation = Command(request_id=str(uuid4()))
    created = repo.create(creation, initial_state, dict)
    game_id, token = created["game_id"], created["game_token"]
    command = Command(request_id=str(uuid4()))
    reservation = repo.reserve(game_id, token, command, "examine", 10)
    summary = repo.claim(game_id, token, "owner")
    assert repo.claim(game_id, token, "owner") == summary
    with pytest.raises(HTTPException, match="ownership_changed"):
        repo.commit(game_id, command, reservation, reservation["state"], {}, dict)
    with pytest.raises(HTTPException, match="수사를 찾을 수 없습니다"):
        repo.create(creation, initial_state, dict)
    access = AccountAccess("owner")
    new_reservation = repo.reserve(game_id, access, command, "examine", 10)
    repo.abort(command, reservation)
    updated = {**new_reservation["state"], "examined": True}
    response = repo.commit(game_id, command, new_reservation, updated, {}, dict)
    assert response["state"]["revision"] == 1
    assert repo.reserve(game_id, access, command, "examine", 10) == {"cached": response}
    assert repo.list_owned("other") == {"items": [], "next_cursor": None}
    assert repo.list_owned("owner")["items"][0]["game_id"] == game_id


def test_concurrent_account_creation_is_idempotent(mongo_repository):
    """같은 계정이 같은 UUID로 수사를 동시에 시작해도 한 번만 생성한다.

    Args:
        mongo_repository: 테스트용 MongoDB 저장소.

    Returns:
        None: 한 계정의 중복과 다른 계정의 충돌을 확인한다.
    """
    repo = mongo_repository
    command = Command(request_id=str(uuid4()))
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(repo.create, command, initial_state, dict, "owner")
        second = pool.submit(repo.create, command, initial_state, dict, "owner")
        assert first.result() == second.result()
        assert first.result()["game_token"] is None
    with pytest.raises(HTTPException, match="수사를 찾을 수 없습니다"):
        repo.create(command, initial_state, dict, "other")
    assert repo.database.investigations.count_documents({}) == 1
    second_game = repo.create(
        Command(request_id=str(uuid4())), initial_state, dict, "owner"
    )
    first_page = repo.list_owned("owner", limit=1)
    second_page = repo.list_owned("owner", cursor=first_page["next_cursor"], limit=1)
    actual = {first_page["items"][0]["game_id"], second_page["items"][0]["game_id"]}
    assert actual == {first.result()["game_id"], second_game["game_id"]}
    assert second_page["next_cursor"] is None


def test_delete_owned_removes_only_owned_games_and_requests(mongo_repository):
    """계정 정리는 자기 게임과 요청을 함께 삭제하고 같은 작업의 재시도를 허용한다.

    Args:
        mongo_repository: 테스트용 MongoDB 저장소.

    Returns:
        None: 대상 소유자만 정리하는지 확인한다.
    """
    repo = mongo_repository
    owned_creation = Command(request_id=str(uuid4()))
    owned = repo.create(owned_creation, initial_state, dict, "owner")
    other = repo.create(Command(request_id=str(uuid4())), initial_state, dict, "other")
    repo.delete_owned("owner")
    repo.delete_owned("owner")
    assert repo.database.investigations.find_one({"_id": owned["game_id"]}) is None
    assert (
        repo.database.investigation_operations.find_one({"game_id": owned["game_id"]})
        is None
    )
    assert repo.get(other["game_id"], AccountAccess("other")) == other["state"]


def test_deleted_owner_cannot_create_or_claim_late(mongo_repository):
    """탈퇴 완료 후 이전 인증 문맥이 수사를 만들거나 연결하지 못한다.

    Args:
        mongo_repository: 테스트용 MongoDB 저장소.

    Returns:
        None: 늦은 요청이 탈퇴 계정의 기록을 만들면 실패한다.
    """
    repo = mongo_repository
    anonymous = repo.create(Command(request_id=str(uuid4())), initial_state, dict)
    repo.delete_owned("deleted")
    with pytest.raises(HTTPException) as create_error:
        repo.create(Command(request_id=str(uuid4())), initial_state, dict, "deleted")
    assert create_error.value.status_code == 401
    with pytest.raises(HTTPException) as claim_error:
        repo.claim(anonymous["game_id"], anonymous["game_token"], "deleted")
    assert claim_error.value.status_code == 401
    assert repo.get(anonymous["game_id"], anonymous["game_token"]) == anonymous["state"]
    assert repo.list_owned("deleted") == {"items": [], "next_cursor": None}


def test_odm_commit_rolls_back_when_response_cannot_be_prepared(mongo_repository):
    """확정 응답 준비가 실패하면 같은 트랜잭션의 수사 변경도 되돌린다.

    Args:
        mongo_repository: 실제 replica set의 테스트 저장소.

    Returns:
        None: 수사 상태와 예약이 함께 롤백되는지 확인한다.
    """

    def broken_present(state):
        """수사 변경 직후 공개 응답 준비에 실패한다.

        Args:
            state: 공개 응답으로 변환할 내부 상태.

        Returns:
            None: 응답 대신 변환 오류를 발생시킨다.
        """
        raise ValueError("응답 변환 실패")

    repo = mongo_repository
    created = repo.create(Command(request_id=str(uuid4())), initial_state, dict)
    game_id, token = created["game_id"], created["game_token"]
    command = Command(request_id=str(uuid4()))
    reservation = repo.reserve(game_id, token, command, "examine", 10)
    changed = reservation["state"]
    changed["examined"].append("evidence")
    with pytest.raises(ValueError, match="응답 변환 실패"):
        repo.commit(game_id, command, reservation, changed, {}, broken_present)
    assert repo.get(game_id, token) == created["state"]
    saved = repo.commit(game_id, command, reservation, changed, {}, dict)
    assert saved["state"]["revision"] == 1
