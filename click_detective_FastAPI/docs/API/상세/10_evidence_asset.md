# 10. 열람한 원본 자료의 이미지

`GET /v1/games/{game_id}/evidence-assets/{evidence_id}`

현재 수사에서 접근 가능한 증거 이미지를 파일로 받는다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`, `evidence_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

## 서버 처리 순서

1. 수사 토큰과 원본 열람 여부를 검사합니다.
2. `evidence_image_path`가 `evidence.json`의 `illustration`을 확인합니다. 비어 있으면 `assets/evidence/{증거ID}.png`를 찾습니다.
3. `data/public` 내부 경로와 파일 존재를 확인합니다. 파일이 없으면 404를 반환합니다.

[2차 조사 이미지와 기존 수사 유지](../../게임진행/2차_증거_이미지.md)를 참고하세요.

## 응답

JSON이 아니라 이미지·영상 파일 응답입니다. content-type·파일 바이트를 사용합니다. Range 요청이면 206 부분 응답이 될 수 있습니다.

## 실패·주의점

- 422: 미열람·미공개 원본.
- 404: 이미지 정보나 파일 없음.
- 클라이언트가 임의 파일 경로를 넘기는 API가 아닙니다.

처리 진입점은 `evidence_asset()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_material_controller.py#L95)
