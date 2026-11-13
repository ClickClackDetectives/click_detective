# app/schemas.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../app/schemas.py)

## 역할과 읽는 순서

행동 입력만 받는 API 형식. 승인 사실·획득 상태·정답을 사용자가 지정하지 못하게 한다.

아래 함수의 입력과 조건을 먼저 읽고 연결된 호출을 원본 소스에서 따라가세요.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## 모듈 설정과 상수

```python
Key = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=128)]
```

이 값은 코드 선언입니다. 실제 .env 비밀값이나 수사 DB 값은 여기에 읽어 넣지 않았습니다.

## DTO

[원본 10번째 줄](../../../app/schemas.py#L10)

오탈자·임의 상태 주입을 막기 위해 정의하지 않은 필드는 거절한다.

## NewGame

[원본 15번째 줄](../../../app/schemas.py#L15)

새 수사 요청. 같은 요청 UUID는 같은 생성 결과를 재사용한다.

### 선언 필드

```python
request_id: UUID
case_id: Key = "thirteenth-bell-v1"
scenario_version: Key
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Command

[원본 22번째 줄](../../../app/schemas.py#L22)

변경 요청의 공통 키. revision은 현재 공개 상태에서 받은 값을 사용한다.

### 선언 필드

```python
request_id: UUID
expected_revision: int = Field(ge=0)
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Examine

[원본 28번째 줄](../../../app/schemas.py#L28)

증거를 열람한다. GET으로 상태를 몰래 변경하지 않는다.

### 선언 필드

```python
evidence_id: Key
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Interrogate

[원본 33번째 줄](../../../app/schemas.py#L33)

사용자 심문 입력. 공개 사실과 필수 사실은 서버가 구성한다.

### 선언 필드

```python
suspect_id: Key
question: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
material_id: Key | None = None
topic_id: Key | None = None
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Source

[원본 41번째 줄](../../../app/schemas.py#L41)

증거·실제로 기록된 진술·실제로 생성된 추론을 구별하는 출처 참조.

### 선언 필드

```python
kind: Literal["evidence", "testimony", "derived"]
id: Key
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Infer

[원본 47번째 줄](../../../app/schemas.py#L47)

2~4개의 실제 출처를 정확한 조합으로 연결한다.

### 선언 필드

```python
sources: list[Source] = Field(min_length=2, max_length=4)
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Advance

[원본 52번째 줄](../../../app/schemas.py#L52)

다음 단계 요청. 값을 대입하지 않고 서버가 조건을 검사한다.

### 선언 필드

```python
target_phase: Literal[2] = 2
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Notes

[원본 57번째 줄](../../../app/schemas.py#L57)

메모 전체 저장. 단계·고발 상태를 포함한 공식 상태는 DB가 담당한다.

### 선언 필드

```python
text: str = Field(max_length=20000)
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

## Accuse

[원본 62번째 줄](../../../app/schemas.py#L62)

고발 선택과 실제 제출할 추론 ID만 받는다.

### 선언 필드

```python
suspect_id: Key
motive: Key
method: Key
evidence_ids: list[Key] = Field(default_factory=list, max_length=50)
```

필드 기본값과 Field 제약은 입력 허용 범위를 뜻합니다. 상속한 필드도 함께 적용됩니다.

