# `app/investigation/controllers/investigation_material_controller.py`

[코드 참조 목차](../../../README.md) · [도메인 목차](../README.md) · [실제 소스](../../../../../app/investigation/controllers/investigation_material_controller.py)

획득 자료, 쟁점과 증거 자산 API.

## `materials`

[소스 선언](../../../../../app/investigation/controllers/investigation_material_controller.py#L17)

```python
def materials(game_id: str, request: Request, kind: str | None=None, archive_kind: str | None=None, search: str='', place: str | None=None):
    ...
```

공개 가능한 목록을 백엔드에서 분류·검색한다. GET은 열람 처리하지 않는다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.
- kind (str | None): 조회할 자료 종류.
- archive_kind (str | None): 자료실 분류 조건. 생략하면 모든 분류를 포함한다.
- search (str): 목록에서 찾을 검색 문자열.
- place (str | None): 조회할 장소 이름 또는 all.

**반환값**

- dict: 분류·장소·검색 조건에 맞는 자료 목록.

## `material_detail`

[소스 선언](../../../../../app/investigation/controllers/investigation_material_controller.py#L57)

```python
def material_detail(game_id: str, material_key: str, request: Request):
    ...
```

획득한 원본·진술·추론만 본문을 제공한다. 접두사로 ID 충돌을 구분한다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- material_key (str): 자료 종류와 ID를 합친 키. 예: evidence:1-01.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- dict: 열람 가능한 원본 자료 또는 획득한 진술·추론의 상세 정보.

## `evidence_asset`

[소스 선언](../../../../../app/investigation/controllers/investigation_material_controller.py#L95)

```python
def evidence_asset(game_id: str, evidence_id: str, request: Request):
    ...
```

원본 자료의 이미지도 열람 조건을 확인한다. 사용자 파일 경로는 받지 않는다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- evidence_id (str): 원본 증거의 식별자.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- FileResponse: 획득 조건과 경로를 검사한 증거 이미지 응답.

## `findings`

[소스 선언](../../../../../app/investigation/controllers/investigation_material_controller.py#L116)

```python
def findings(game_id: str, request: Request):
    ...
```

이미 발견된 쟁점만 반환한다. 미발견 조건·정답 목록은 공개하지 않는다.

**인자**

- game_id (str): 조회하거나 변경할 수사의 식별자.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

- dict: 이미 발견한 쟁점 목록을 담은 findings 항목.
