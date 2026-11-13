# app/dialogue/schemas.py 상세 설명

[문서 목차](../../../README.md) · [파일별 목차](../../README.md) · [현재 소스](../../../../app/dialogue/schemas.py)

## 역할과 읽는 순서

API의 JSON 형식과 검증 규칙.

Pydantic은 JSON을 아래 클래스의 객체로 바꾸면서 타입과 길이를 검사한다.
DTO(Data Transfer Object)는 서버 사이에서 주고받는 데이터의 형식을 뜻한다.
필드의 description은 /docs에도 표시된다.

아래 함수의 입력과 조건을 먼저 읽고 연결된 호출을 원본 소스에서 따라가세요.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
Text = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)
]
Identifier = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)
]
FactText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)
]
ReplyText = Annotated[str, StringConstraints(min_length=1, max_length=12000)]
FinishReason = Literal["stop", "fixed", "fallback"]
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## DTO

[원본 27번째 줄](../../../../app/dialogue/schemas.py#L27)

모든 API 모델의 공통 규칙: 정의하지 않은 JSON 필드는 거절한다.

## Persona

[원본 33번째 줄](../../../../app/dialogue/schemas.py#L33)

이번 답변을 할 인물의 공개 프로필과 말투.

### 선언 필드

```python
name: Identifier = Field(description="시나리오에 등록된 인물 이름")
role: Identifier = Field(description="인물의 역할. 예: 주치의")
speech_style: Text = Field(description="말투 지침. 예: 절제된 존댓말")
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Material

[원본 41번째 줄](../../../../app/dialogue/schemas.py#L41)

Next.js가 이번 심문에 제시하도록 승인한 원본 자료 또는 추론.

### 선언 필드

```python
kind: Literal["evidence", "inference"] = Field(description="원본 증거 또는 추론")
id: Identifier = Field(description="자료의 내부 식별자")
code: Identifier = Field(description="화면에 표시하는 자료 번호")
title: Identifier = Field(description="자료 제목")
allowed_text: Text = Field(description="이번 답변에서 사용할 수 있도록 선별한 설명")
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Fact

[원본 51번째 줄](../../../../app/dialogue/schemas.py#L51)

게임 규칙이 공개를 승인한 사실. local 모드는 의미를 보존해 재서술할 수 있다.

### 선언 필드

```python
id: Identifier = Field(description="Next.js의 승인 계획과 대조할 사실 ID")
text: FactText = Field(description="생성 대사의 의미 검증 기준이 되는 승인 사실 원문")
nature: Literal["본인 진술", "직접 목격", "전언", "추측/인상", "심문에서 인정"] = Field(
        description="사실의 성격. 모든 진술을 자백으로 취급하지 않는다"
    )
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## History

[원본 61번째 줄](../../../../app/dialogue/schemas.py#L61)

선택 인물과 나눈 이전 대화 한 건. local 모드에서 최근 일부를 문맥으로 사용한다.

### 선언 필드

```python
role: Literal["user", "suspect"] = Field(description="질문자 또는 심문 대상")
text: Text = Field(description="실제로 제공했던 질문 또는 답변")
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## CharacterReplyRequest

[원본 68번째 줄](../../../../app/dialogue/schemas.py#L68)

Next.js가 검증한 심문 문맥. 게임 상태를 수정하라는 명령은 아니다.

required_fact_ids는 allowed_facts 안에 있어야 한다. state_revision은
응답에 그대로 돌려주며, 최신 게임 상태인지 최종 확인하는 책임은 Next.js에 있다.

### 선언 필드

```python
request_id: UUID = Field(description="재시도 시에도 유지할 요청 UUID")
game_id: Identifier = Field(description="Next.js가 쿠키로 확인한 수사 ID")
case_id: Identifier = Field(description="사건 ID. 수사 ID와 다르다")
scenario_version: Identifier = Field(description="서버가 사용하는 시나리오 스냅샷 버전")
state_revision: int = Field(ge=0, description="요청을 계획한 시점의 게임 상태 버전")
turn_index: int = Field(ge=1, le=25, description="확정 전 질문 횟수 + 1")
suspect_id: Identifier = Field(description="심문할 인물의 내부 ID")
phase: Literal[1, 2] = Field(description="현재 조사 단계")
question: Text = Field(description="질문 원문")
topic_id: Identifier | None = Field(default=None, description="동선·관계 질문의 주제 ID")
persona: Persona = Field(description="선택 인물의 프로필과 말투")
presented_materials: list[Material] = Field(
        default_factory=list, max_length=30, description="제시하도록 승인된 자료"
    )
allowed_facts: list[Fact] = Field(
        default_factory=list, max_length=10, description="이번 대사에 포함할 승인 사실 목록"
    )
required_fact_ids: list[Identifier] = Field(
        default_factory=list, max_length=10, description="반드시 포함해야 하는 사실의 ID"
    )
history: list[History] = Field(
        default_factory=list, max_length=20, description="해당 인물의 제한된 최근 대화"
    )
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## CharacterReplyRequest.validate_fact_references

[원본 105번째 줄](../../../../app/dialogue/schemas.py#L105)

사실 ID 중복과 필수 ID의 허용 범위 포함 여부를 검사한다.

### 입력과 처리

```python
def validate_fact_references(self) -> "CharacterReplyRequest":
```

주요 분기 조건은 `len(allowed_fact_ids) != len(unique_allowed_ids)`, `len(self.required_fact_ids) != len(unique_required_ids)`, `not unique_required_ids.issubset(unique_allowed_ids)`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def validate_fact_references(self) -> "CharacterReplyRequest":
        """사실 ID 중복과 필수 ID의 허용 범위 포함 여부를 검사한다."""
        allowed_fact_ids = [fact.id for fact in self.allowed_facts]
        unique_allowed_ids = set(allowed_fact_ids)
        unique_required_ids = set(self.required_fact_ids)

        if len(allowed_fact_ids) != len(unique_allowed_ids):
            raise ValueError("Duplicate allowed fact IDs")
        if len(self.required_fact_ids) != len(unique_required_ids):
            raise ValueError("Duplicate required fact IDs")
        if not unique_required_ids.issubset(unique_allowed_ids):
            raise ValueError("Required facts must be allowed")
        return self
````

## CharacterReplyResponse

[원본 120번째 줄](../../../../app/dialogue/schemas.py#L120)

최종 대사와 검증용 식별 정보. 프롬프트나 전체 게임 상태는 포함하지 않는다.

### 선언 필드

```python
request_id: UUID = Field(description="요청과 같은 UUID")
suspect_id: Identifier = Field(description="요청과 같은 인물 ID")
state_revision: int = Field(ge=0, description="요청과 같은 게임 상태 버전")
reply: ReplyText = Field(description="local 모드에서는 의미 검증된 생성 대사, fixed/fallback에서는 승인 원문 조립 대사")
used_fact_ids: list[Identifier] = Field(description="최종 대사에 사용한 사실 ID 목록")
model_version: Identifier = Field(description="모델 및 적용 어댑터 식별자 또는 fixed-v1")
finish_reason: FinishReason = Field(
        description="stop: 모델 생성 및 검증 성공, fixed: 고정 모드, fallback: 모델 실패 후 고정 대체"
    )
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

