# 05. 소개·인물 이미지·영상

`GET /v1/assets/{asset_path:path}`

사건 소개에 쓰이는 이미지·영상 등 공개 파일을 가져온다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다.

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

처리 진입점은 `public_asset()`이다. [컨트롤러 소스](../../../app/cases/controllers/cases_controller.py#L58)
