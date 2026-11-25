"""새 MongoDB 수사 컬렉션의 최소 BSON 계약을 정의한다."""

from pymongo.errors import OperationFailure

NONNEGATIVE = {"bsonType": ["int", "long"], "minimum": 0}
STRING_OR_NULL = {"bsonType": ["string", "null"]}
DATE_OR_NULL = {"bsonType": ["date", "null"]}
GAME_FIELDS = {
    "_id": {"bsonType": "string"},
    "owner_user_id": STRING_OR_NULL,
    "anonymous_token_hash": STRING_OR_NULL,
    "case_id": {"bsonType": "string"},
    "scenario_version": {"bsonType": "string"},
    "schema_version": {"bsonType": "int", "minimum": 1},
    "ownership_version": NONNEGATIVE,
    "revision": NONNEGATIVE,
    "state": {"bsonType": "object"},
    "updated_at": {"bsonType": "date"},
}
OPERATION_FIELDS = {
    "_id": {"bsonType": "string"},
    "game_id": {"bsonType": "string"},
    "digest": {"bsonType": "string"},
    "status": {"enum": ["pending", "failed", "complete"]},
    "nonce": STRING_OR_NULL,
    "lease_until": DATE_OR_NULL,
    "response": {"bsonType": ["object", "null"]},
    "completed_at": DATE_OR_NULL,
    "creation_owner_user_id": STRING_OR_NULL,
}


def ensure_collection(database, name, fields, conditions):
    """컬렉션이 처음 만들어질 때 문서 validator를 설정한다.

    Args:
        database: 해당 컬렉션을 저장할 MongoDB 데이터베이스.
        name: 컬렉션 이름.
        fields: 반드시 존재해야 하는 필드와 BSON 스키마.
        conditions: 필드 사이에 추가로 성립해야 하는 조회 조건.

    Returns:
        None: 신규 컬렉션을 만들거나 기존 컬렉션을 그대로 사용한다.
    """
    schema = {"bsonType": "object", "required": list(fields), "properties": fields}
    try:
        database.create_collection(
            name,
            check_exists=False,
            validator={"$and": [{"$jsonSchema": schema}, conditions]},
        )
    except OperationFailure as error:
        if error.code != 48:
            raise


def prepare_collections(database):
    """수사와 행동 요청 컬렉션을 준비한다.

    Args:
        database: 수사 저장에 사용할 MongoDB 데이터베이스.

    Returns:
        None: 두 컬렉션의 최초 생성 작업을 마친다.
    """
    ensure_collection(
        database,
        "investigations",
        GAME_FIELDS,
        {
            "$or": [
                {"owner_user_id": None, "anonymous_token_hash": {"$type": "string"}},
                {"owner_user_id": {"$type": "string"}, "anonymous_token_hash": None},
            ]
        },
    )
    ensure_collection(
        database,
        "investigation_operations",
        OPERATION_FIELDS,
        {
            "$or": [
                {"status": "failed"},
                {
                    "status": "pending",
                    "nonce": {"$type": "string"},
                    "lease_until": {"$type": "date"},
                },
                {"status": "complete", "response": {"$type": "object"}},
            ]
        },
    )

    ensure_collection(
        database,
        "investigation_owners",
        {
            "_id": {"bsonType": "string"},
            "blocked": {"bsonType": "bool"},
            "sequence": NONNEGATIVE,
        },
        {"blocked": {"$exists": True}},
    )
