# `app/cases/routes.py`

[코드 참조 목차](../../README.md) · [전체 문서 목차](../../../README.md) · [실제 소스](../../../../app/cases/routes.py)

> 현재 소스 기준: 2026-11-16. 파일 길이: 72줄. 선언문 아래의 설명은 실제 docstring을 기준으로 정리했다.

## 파일의 역할

사건과 공개 자산 API.

## 함께 읽을 코드

- [app/dependencies.py](../dependencies.md)

## `catalog`

[소스 선언 위치](../../../../app/cases/routes.py#L12)

```python
async def catalog(request: Request):
    ...
```

초기 화면 데이터 전체를 공개 DTO로 반환한다.

**파라미터**

- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

dict: 초기 화면에 사용할 공개 사건·인물·자료 정보.

## `cases`

[소스 선언 위치](../../../../app/cases/routes.py#L25)

```python
async def cases(request: Request):
    ...
```

실제로 시작 가능한 사건만 반환한다.

**파라미터**

- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

dict: 시작할 수 있는 사건 ID, 버전과 소개의 목록.

## `case_detail`

[소스 선언 위치](../../../../app/cases/routes.py#L47)

```python
async def case_detail(case_id: str, request: Request):
    ...
```

사건 소개·인물·공개 콘텐츠를 반환한다. 비공개 규칙은 제외한다.

**파라미터**

- case_id (str): 조회하거나 생성할 사건의 식별자.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

dict: 지정 사건의 공개 카탈로그.

## `public_asset`

[소스 선언 위치](../../../../app/cases/routes.py#L62)

```python
async def public_asset(asset_path: str, request: Request):
    ...
```

소개·인물 이미지·영상만 제공한다. 증거 이미지는 수사 권한 경로로 제공한다.

**파라미터**

- asset_path (str): 공개 자산의 상대 경로.
- request (Request): 앱 서비스와 인증·수사 토큰 헤더에 접근할 HTTP 요청.

**반환값**

FileResponse: 공개 자산 파일의 HTTP 응답.
