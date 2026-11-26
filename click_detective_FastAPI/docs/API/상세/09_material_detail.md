# 09. 획득한 자료 본문

`GET /v1/games/{game_id}/materials/{material_key}`

현재 수사에서 열람 가능한 자료의 본문을 가져온다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`, `material_key`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

## 서버 처리 순서

1. kind:ID 형식과 evidence/testimony/derived를 검사합니다.
2. 실제 열람·기록·생성 여부를 확인합니다.
3. 원본은 body·illustration, 진술은 excerpt 등 저장 구조, 추론은 body·출처를 반환합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

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

처리 진입점은 `material_detail()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_material_controller.py#L57)
