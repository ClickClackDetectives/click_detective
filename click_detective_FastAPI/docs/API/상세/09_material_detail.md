# 09. 획득한 자료 본문

[API 목차](README.md) · [공통 규칙](../공통규칙.md)

## 역할과 호출 시점

`GET /v1/games/{game_id}/materials/{material_key}`

획득한 자료 본문에 사용하는 실제 구현 경로입니다. 공개 상태나 파일을 조회합니다. GET은 게임 상태를 변경하지 않습니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다. 수사별 `X-Game-Token: <생성 응답의 game_token>`도 필요합니다.

## 입력

경로 값: `game_id`, `material_key`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

## 서버 처리 순서

1. kind:ID 형식과 evidence/testimony/derived를 검사합니다.
2. 실제 열람·기록·생성 여부를 확인합니다.
3. 원본은 body·illustration, 진술은 excerpt 등 저장 구조, 추론은 body·출처를 반환합니다.

## 응답

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

```json
{
  "kind": "evidence",
  "id": "1-01",
  "body": "실제 자료 원문",
  "illustration": "/v1/games/수사UUID/evidence-assets/1-01"
}
```

이미지 파일이 없는 원본 자료의 `illustration`은 `null`입니다. 없는 파일의 이미지 주소를 반환하지 않습니다.

## 실패·주의점

- 422: 접두사 형식·미획득·현재 단계와 맞지 않는 원본.
- 진술 상세는 body 대신 excerpt를 사용합니다.
- 자료 키의 콜론은 필요에 따라 URL 인코딩합니다.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

현재 API 진입점은 [app/investigation/api/material_routes.py의 `material_detail`](../../../app/investigation/api/material_routes.py#L52)다.

처리 순서는 [GameService](../../코드참조/app/investigation/service.md), 저장 조건은 [수사 저장](../../서버/수사_저장.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/views/presentation.md)에서 확인한다.
