# `app/dialogue/services/preprocess_agent/dialogue_preprocess_prompt.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/dialogue/services/preprocess_agent/dialogue_preprocess_prompt.py)

생성 모델이 읽을 질문과 승인 사실을 준비한다.

## `normalize_question`

[소스 선언](../../../../../../app/dialogue/services/preprocess_agent/dialogue_preprocess_prompt.py#L31)

```python
def normalize_question(text: str) -> str:
    ...
```

유니코드 표기를 통일하고 중복 공백을 줄인다. 공개 권한을 새로 부여하지 않는다.

**인자**

- text (str): 정규화하거나 의미 단서를 추출할 원문 문자열.

**반환값**

- str: 유니코드 표기와 공백을 정리한 질문.

## `build_messages`

[소스 선언](../../../../../../app/dialogue/services/preprocess_agent/dialogue_preprocess_prompt.py#L43)

```python
def build_messages(request: CharacterReplyRequest, settings: Settings, *, units: list[VerificationUnit] | None=None) -> list[dict[str, str]]:
    ...
```

서버가 승인한 사실을 인물·질문과 함께 JSON 데이터로 전달한다.

요청·게임 식별자나 시나리오 전체는 프롬프트에 넣지 않는다. 이력은 최근 일부만
남기고, 모델 토큰 예산 초과 시 runtime에서 요청을 거절하며 사실은 자르지 않는다.

**인자**

- request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
- settings (Settings): 생성 프롬프트에 사용할 설정.
- units: 요청의 승인 사실을 전처리에서 분리한 검증 문장. 생략 시 여기서 분리한다.

**반환값**

- list[dict[str, str]]: 인물·질문·승인 사실을 담은 생성용 프롬프트.
