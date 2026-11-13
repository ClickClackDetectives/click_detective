# 10. 열람한 원본 자료의 이미지

[API 목차](README.md) · [공통 규칙](../06_API_공통규칙과_전체목록.md)

## 역할과 호출 시점

`GET /v1/games/{game_id}/evidence-assets/{evidence_id}`

열람한 원본 자료의 이미지에 사용하는 실제 구현 경로입니다. 공개 상태나 파일을 조회합니다. GET은 게임 상태를 변경하지 않습니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다. 수사별 `X-Game-Token: <생성 응답의 game_token>`도 필요합니다.

## 입력

경로 값: `game_id`, `evidence_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

## 서버 처리 순서

1. 수사 토큰과 원본 열람 여부를 검사합니다.
2. evidence.json의 illustration을 서버에서 선택합니다.
3. data/public 내부 경로와 파일 존재를 확인합니다.

## 응답

JSON이 아니라 이미지·영상 파일 응답입니다. content-type·파일 바이트를 사용합니다. Range 요청이면 206 부분 응답이 될 수 있습니다.

## 실패·주의점

- 422: 미열람·미공개 원본.
- 404: 이미지 정보나 파일 없음.
- 클라이언트가 임의 파일 경로를 넘기는 API가 아닙니다.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

[app/main.py의 evidence_asset()](../../app/main.py#L144)에서 시작합니다. 생성·변경은 [GameService](../파이썬_파일별_상세/app/service.md), 저장은 [Repository](../파이썬_파일별_상세/app/repository.md), 화면 상태는 [Presenter](../파이썬_파일별_상세/app/presentation.md)를 확인하세요.
