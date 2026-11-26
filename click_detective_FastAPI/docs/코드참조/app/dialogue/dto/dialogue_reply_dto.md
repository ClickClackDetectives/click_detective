# `app/dialogue/dto/dialogue_reply_dto.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/dialogue/dto/dialogue_reply_dto.py)

API의 JSON 형식과 검증 규칙.

Pydantic은 JSON을 아래 클래스의 객체로 바꾸면서 타입과 길이를 검사한다.
DTO(Data Transfer Object)는 서버 사이에서 주고받는 데이터의 형식을 뜻한다.
필드의 description은 /docs에도 표시된다.

## `DTO`

[소스 선언](../../../../../app/dialogue/dto/dialogue_reply_dto.py#L34)

```python
class DTO(BaseModel):
    ...
```

모든 API 모델의 공통 규칙: 정의하지 않은 JSON 필드는 거절한다.

**인자**

- 없음.

**반환값**

- DTO: 위 역할을 수행하도록 생성된 객체.

## `Persona`

[소스 선언](../../../../../app/dialogue/dto/dialogue_reply_dto.py#L47)

```python
class Persona(DTO):
    ...
```

이번 답변을 할 인물의 공개 프로필과 말투.

**인자**

- name (Identifier): 시나리오에 등록된 인물 이름
- role (Identifier): 인물의 역할. 예: 주치의
- speech_style (Text): 말투 지침. 예: 절제된 존댓말

**반환값**

- Persona: 위 역할을 수행하도록 생성된 객체.

## `Material`

[소스 선언](../../../../../app/dialogue/dto/dialogue_reply_dto.py#L64)

```python
class Material(DTO):
    ...
```

서버가 이번 심문에 제시하도록 승인한 원본 자료 또는 추론.

**인자**

- kind (Literal['evidence', 'inference']): 원본 증거 또는 추론
- id (Identifier): 자료의 내부 식별자
- code (Identifier): 화면에 표시하는 자료 번호
- title (Identifier): 자료 제목
- allowed_text (Text): 이번 답변에서 사용할 수 있도록 선별한 설명

**반환값**

- Material: 위 역할을 수행하도록 생성된 객체.

## `Fact`

[소스 선언](../../../../../app/dialogue/dto/dialogue_reply_dto.py#L85)

```python
class Fact(DTO):
    ...
```

게임 규칙이 공개를 승인한 사실. local 모드는 의미를 보존해 재서술할 수 있다.

**인자**

- id (Identifier): 서버의 승인 계획과 대조할 사실 ID
- text (FactText): 생성 대사의 의미 검증 기준이 되는 승인 사실 원문
- nature (Literal['본인 진술', '직접 목격', '전언', '추측/인상', '심문에서 인정']): 사실의 성격. 모든 진술을 자백으로 취급하지 않는다

**반환값**

- Fact: 위 역할을 수행하도록 생성된 객체.

## `History`

[소스 선언](../../../../../app/dialogue/dto/dialogue_reply_dto.py#L106)

```python
class History(DTO):
    ...
```

선택 인물과 나눈 이전 대화 한 건. local 모드에서 최근 일부를 문맥으로 사용한다.

**인자**

- role (Literal['user', 'suspect']): 질문자 또는 심문 대상
- text (Text): 실제로 제공했던 질문 또는 답변

**반환값**

- History: 위 역할을 수행하도록 생성된 객체.

## `CharacterReplyRequest`

[소스 선언](../../../../../app/dialogue/dto/dialogue_reply_dto.py#L121)

```python
class CharacterReplyRequest(DTO):
    ...
```

서버가 승인한 심문 문맥. 게임 상태를 수정하라는 명령은 아니다.

required_fact_ids는 allowed_facts 안에 있어야 한다. state_revision은
응답에 그대로 돌려주며, 저장 시 최신 게임 상태인지는 수사 저장소가 다시 확인한다.

**인자**

- request_id (UUID): 재시도 시에도 유지할 요청 UUID
- game_id (Identifier): 서버가 확인한 수사 ID
- case_id (Identifier): 사건 ID. 수사 ID와 다르다
- scenario_version (Identifier): 서버가 사용하는 시나리오 스냅샷 버전
- state_revision (int): 요청을 계획한 시점의 게임 상태 버전
- turn_index (int): 확정 전 질문 횟수 + 1
- suspect_id (Identifier): 심문할 인물의 내부 ID
- phase (Literal[1, 2]): 현재 조사 단계
- question (Text): 질문 원문
- topic_id (Identifier | None): 동선·관계 질문의 주제 ID
- persona (Persona): 선택 인물의 프로필과 말투
- presented_materials (list[Material]): 제시하도록 승인된 자료
- allowed_facts (list[Fact]): 이번 대사에 포함할 승인 사실 목록
- required_fact_ids (list[Identifier]): 반드시 포함해야 하는 사실의 ID
- history (list[History]): 해당 인물의 제한된 최근 대화

**반환값**

- CharacterReplyRequest: 위 역할을 수행하도록 생성된 객체.

## `CharacterReplyRequest.validate_fact_references`

[소스 선언](../../../../../app/dialogue/dto/dialogue_reply_dto.py#L189)

```python
def validate_fact_references(self) -> 'CharacterReplyRequest':
    ...
```

사실 ID 중복과 필수 ID의 허용 범위 포함 여부를 검사한다.

**인자**

- 없음.

**반환값**

- CharacterReplyRequest: 사실 ID 중복과 필수 ID의 승인 범위를 확인한 요청 자신.

## `CharacterReplyResponse`

[소스 선언](../../../../../app/dialogue/dto/dialogue_reply_dto.py#L211)

```python
class CharacterReplyResponse(DTO):
    ...
```

최종 대사와 검증용 식별 정보. 프롬프트나 전체 게임 상태는 포함하지 않는다.

**인자**

- request_id (UUID): 요청과 같은 UUID
- suspect_id (Identifier): 요청과 같은 인물 ID
- state_revision (int): 요청과 같은 게임 상태 버전
- reply (ReplyText): local 모드에서는 의미 검증된 생성 대사, fixed/fallback에서는 승인 원문 조립 대사
- used_fact_ids (list[Identifier]): 최종 대사에 사용한 사실 ID 목록
- model_version (Identifier): 모델 및 적용 어댑터 식별자 또는 fixed-v1
- finish_reason (FinishReason): 성공, 고정, 복구, 부분 응답 또는 중립 답변.

**반환값**

- CharacterReplyResponse: 위 역할을 수행하도록 생성된 객체.
