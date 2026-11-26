# `app/investigation/repositories/investigation_mongo_documents.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/repositories/investigation_mongo_documents.py)

기존 BSON 수사 저장 구조를 MongoEngine 문서로 매핑한다.

## `InvestigationDocument`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_documents.py#L13)

```python
class InvestigationDocument(Document):
    ...
```

수사 소유권과 상태 스냅샷을 기존 컬렉션에 매핑한다.

**인자**

- id: 수사 UUID.
- owner_user_id: 계정 UUID 또는 익명 수사의 None.
- anonymous_token_hash: 익명 수사 토큰 해시 또는 계정 수사의 None.
- case_id: 사건 ID.
- scenario_version: 초기 사건 스냅샷 버전.
- schema_version: 수사 저장 구조 버전.
- ownership_version: 소유권 변경 순번.
- revision: 플레이 상태 변경 순번.
- state: 기존 수사 상태 JSON.
- updated_at: 마지막 갱신 시각.
- reservation_sequence: 예약과 소유권을 직렬화하는 저장소 내부 순번.
- commit_sequence: 확정을 직렬화하는 저장소 내부 순번.

**반환값**

- InvestigationDocument: MongoDB의 수사 문서를 나타내는 모델.

## `OperationDocument`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_documents.py#L53)

```python
class OperationDocument(Document):
    ...
```

수사 요청의 예약과 캐시된 확정 결과를 매핑한다.

**인자**

- id: 요청 UUID.
- game_id: 요청이 적용되는 수사 UUID.
- digest: 정규화한 요청 내용의 해시.
- status: pending, failed 또는 complete.
- nonce: 현재 예약 ID 또는 None.
- lease_until: 실행권 임대 만료 시각 또는 None.
- response: 확정 응답 스냅샷 또는 None.
- completed_at: 확정 시각 또는 원본 자료에서 확인할 수 없는 경우 None.
- creation_owner_user_id: 새 계정 수사의 생성 주체 또는 None.
- ownership_version: 예약 시점의 수사 소유권 버전.

**반환값**

- OperationDocument: MongoDB에 저장할 요청 문서를 나타내는 모델.

## `OwnerDocument`

[소스 선언](../../../../../app/investigation/repositories/investigation_mongo_documents.py#L89)

```python
class OwnerDocument(Document):
    ...
```

탈퇴 뒤에도 수사 소유권 쓰기를 막을 계정 경계를 매핑한다.

**인자**

- id: 인증 계정 UUID.
- blocked: 계정의 생성·연결이 영구 차단됐는지 여부.
- sequence: 계정별 소유권 쓰기를 직렬화하는 저장소 내부 순번.

**반환값**

- OwnerDocument: MongoDB의 계정별 소유권 차단 모델.
