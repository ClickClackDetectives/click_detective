# 11. 발견한 쟁점 조회

[API 목차](README.md) · [공통 규칙](../06_API_공통규칙과_전체목록.md)

## 역할과 호출 시점

`GET /v1/games/{game_id}/findings`

발견한 쟁점 조회에 사용하는 실제 구현 경로입니다. 공개 상태나 파일을 조회합니다. GET은 게임 상태를 변경하지 않습니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다. 수사별 `X-Game-Token: <생성 응답의 game_token>`도 필요합니다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

## 서버 처리 순서

1. 게임 토큰·버전을 확인합니다.
2. state.findingDetails만 반환합니다.

## 응답

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

```json
{
  "findings": [
    {
      "title": "발견한 쟁점 제목",
      "suspectId": "kang",
      "sourceRefs": [
        {
          "kind": "evidence",
          "id": "1-02"
        }
      ],
      "messageIndex": 1
    }
  ]
}
```

## 실패·주의점

- 아직 발견하지 않은 쟁점의 label·need·reply를 공개하지 않습니다.
- 직접 쟁점을 추가하는 POST는 없습니다. 심문 결과로만 확정합니다.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

[app/main.py의 findings()](../../app/main.py#L156)에서 시작합니다. 생성·변경은 [GameService](../파이썬_파일별_상세/app/service.md), 저장은 [Repository](../파이썬_파일별_상세/app/repository.md), 화면 상태는 [Presenter](../파이썬_파일별_상세/app/presentation.md)를 확인하세요.
