# `app/investigation/services/views/investigation_screen_views.py`

[코드 참조 목차](../../../../README.md) · [도메인 목차](../../README.md) · [실제 소스](../../../../../../app/investigation/services/views/investigation_screen_views.py)

원본 Next.js 자료실의 검색·분류 결과를 FastAPI에서 구성하는 표시 전용 서비스.

## `ScreenViews`

[소스 선언](../../../../../../app/investigation/services/views/investigation_screen_views.py#L4)

```python
class ScreenViews:
    ...
```

게임 규칙을 바꾸지 않고 같은 상태를 원본 화면이 요구하는 목록으로 변환한다.

**인자**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- presenter: 내부 상태를 화면용 정보로 변환하는 객체.

**반환값**

- ScreenViews: 위 역할을 수행하도록 생성된 객체.

## `ScreenViews.__init__`

[소스 선언](../../../../../../app/investigation/services/views/investigation_screen_views.py#L15)

```python
def __init__(self, catalog, presenter):
    ...
```

사건 원본과 공개 상태 변환기를 받아 중복된 프런트엔드 데이터 처리를 없앤다.

**인자**

- catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
- presenter: 내부 상태를 화면용 정보로 변환하는 객체.

**반환값**

- None: 필요한 설정과 초기값을 저장한다.

## `ScreenViews.evidence`

[소스 선언](../../../../../../app/investigation/services/views/investigation_screen_views.py#L27)

```python
def evidence(self, state, search='', place='all'):
    ...
```

물증·문서를 장소별로 분류한다. 검색은 원본의 공백·대소문자 동작을 유지한다.

**인자**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- search: 목록에서 찾을 검색 문자열.
- place: 조회할 장소 이름 또는 all.

**반환값**

- dict: 화면에서 보여줄 자료·장소·그룹과 열람 개수.

## `ScreenViews.testimonies`

[소스 선언](../../../../../../app/investigation/services/views/investigation_screen_views.py#L65)

```python
def testimonies(self, state, search='', person='all'):
    ...
```

최초 진술·집사 문서·획득 증언·질문/답변 쌍을 원본 화면과 같은 순서로 검색한다.

**인자**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- search: 목록에서 찾을 검색 문자열.
- person: 조회할 인물 식별자 또는 all.

**반환값**

- dict: 검색과 인물 조건에 맞는 초기 진술·획득 증언·대화 쌍.

## `ScreenViews.inference`

[소스 선언](../../../../../../app/investigation/services/views/investigation_screen_views.py#L182)

```python
def inference(self, state, search='', category='evidence'):
    ...
```

획득한 실제 출처를 자료 종류와 검색어로 골라 원본 추론 선택창에 제공한다.

**인자**

- state: 질문·대화·획득 자료를 담은 현재 수사 상태.
- search: 목록에서 찾을 검색 문자열.
- category: 조회할 자료 분류.

**반환값**

- dict: 자료 분류와 검색 조건에 맞는 획득 출처 목록.
