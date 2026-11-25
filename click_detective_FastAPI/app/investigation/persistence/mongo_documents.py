"""기존 BSON 수사 저장 구조를 MongoEngine 문서로 매핑한다."""

from mongoengine import (
    BooleanField,
    DateTimeField,
    DictField,
    Document,
    IntField,
    StringField,
)


class InvestigationDocument(Document):
    """수사 소유권과 상태 스냅샷을 기존 컬렉션에 매핑한다.

    Args:
        id: 수사 UUID.
        owner_user_id: 계정 UUID 또는 익명 수사의 None.
        anonymous_token_hash: 익명 수사 토큰 해시 또는 계정 수사의 None.
        case_id: 사건 ID.
        scenario_version: 초기 사건 스냅샷 버전.
        schema_version: 수사 저장 구조 버전.
        ownership_version: 소유권 변경 순번.
        revision: 플레이 상태 변경 순번.
        state: 기존 수사 상태 JSON.
        updated_at: 마지막 갱신 시각.
        reservation_sequence: 예약과 소유권을 직렬화하는 저장소 내부 순번.
        commit_sequence: 확정을 직렬화하는 저장소 내부 순번.

    Returns:
        InvestigationDocument: MongoDB의 수사 문서를 나타내는 모델.
    """

    meta = {
        "collection": "investigations",
        "auto_create_index": False,
        "indexes": [("owner_user_id", "-updated_at", "-id")],
    }
    id = StringField(primary_key=True)
    owner_user_id = StringField(null=True)
    anonymous_token_hash = StringField(null=True)
    case_id = StringField(required=True)
    scenario_version = StringField(required=True)
    schema_version = IntField(required=True, min_value=1)
    ownership_version = IntField(required=True, min_value=0)
    revision = IntField(required=True, min_value=0)
    state = DictField(required=True)
    updated_at = DateTimeField(required=True)
    reservation_sequence = IntField(min_value=0)
    commit_sequence = IntField(min_value=0)


class OperationDocument(Document):
    """수사 요청의 예약과 캐시된 확정 결과를 매핑한다.

    Args:
        id: 요청 UUID.
        game_id: 요청이 적용되는 수사 UUID.
        digest: 정규화한 요청 내용의 해시.
        status: pending, failed 또는 complete.
        nonce: 현재 예약 ID 또는 None.
        lease_until: 실행권 임대 만료 시각 또는 None.
        response: 확정 응답 스냅샷 또는 None.
        completed_at: 확정 시각 또는 원본 자료에서 확인할 수 없는 경우 None.
        creation_owner_user_id: 새 계정 수사의 생성 주체 또는 None.
        ownership_version: 예약 시점의 수사 소유권 버전.

    Returns:
        OperationDocument: MongoDB에 저장할 요청 문서를 나타내는 모델.
    """

    meta = {
        "collection": "investigation_operations",
        "auto_create_index": False,
        "indexes": ["game_id"],
    }
    id = StringField(primary_key=True)
    game_id = StringField(required=True)
    digest = StringField(required=True)
    status = StringField(required=True, choices=("pending", "failed", "complete"))
    nonce = StringField(null=True)
    lease_until = DateTimeField(null=True)
    response = DictField(null=True)
    completed_at = DateTimeField(null=True)
    creation_owner_user_id = StringField(null=True)
    ownership_version = IntField(min_value=0)


class OwnerDocument(Document):
    """탈퇴 뒤에도 수사 소유권 쓰기를 막을 계정 경계를 매핑한다.

    Args:
        id: 인증 계정 UUID.
        blocked: 계정의 생성·연결이 영구 차단됐는지 여부.
        sequence: 계정별 소유권 쓰기를 직렬화하는 저장소 내부 순번.

    Returns:
        OwnerDocument: MongoDB의 계정별 소유권 차단 모델.
    """

    meta = {"collection": "investigation_owners", "auto_create_index": False}
    id = StringField(primary_key=True)
    blocked = BooleanField(required=True)
    sequence = IntField(required=True, min_value=0)
