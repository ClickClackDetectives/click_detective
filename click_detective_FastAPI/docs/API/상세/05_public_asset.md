# 05. 소개·인물 이미지·영상

[API 목차](README.md) · [공통 규칙](../공통규칙.md)

## 역할과 호출 시점

`GET /v1/assets/{asset_path:path}`

소개·인물 이미지·영상에 사용하는 실제 구현 경로입니다. 공개 상태나 파일을 조회합니다. GET은 게임 상태를 변경하지 않습니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다.

## 입력

경로 값: `asset_path`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

예: `/v1/assets/assets/characters/kang-minho-live.png`. 앞의 assets는 API 그룹이고 뒤의 assets는 public 내부 실제 폴더이므로 중복이 오타가 아닙니다. 영상은 `Range: bytes=0-99` 같은 요청을 사용할 수 있습니다.

## 서버 처리 순서

1. data/public 내부의 실제 경로인지 resolve()로 확인합니다.
2. assets/evidence/ 아래는 이 공개 경로에서 차단합니다.
3. 허용 확장자 png/jpg/jpeg/webp/mp4/svg와 파일 존재를 검사합니다.
4. FileResponse로 파일을 보내며 지원 환경에서 Range 부분 응답을 사용할 수 있습니다.

## 응답

JSON이 아니라 이미지·영상 파일 응답입니다. content-type·파일 바이트를 사용합니다. Range 요청이면 206 부분 응답이 될 수 있습니다.

## 실패·주의점

- 404: 경로 이탈·증거 폴더·허용하지 않은 확장자·없는 파일.
- 서비스 인증은 필요하므로 브라우저 표시에는 인증 프록시가 필요합니다.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

현재 API 진입점은 [app/cases/routes.py의 `public_asset`](../../../app/cases/routes.py#L62)다.

처리 순서는 [GameService](../../코드참조/app/investigation/service.md), 저장 조건은 [수사 저장](../../서버/수사_저장.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/views/presentation.md)에서 확인한다.
