# 08. 자료 목록·서버 필터·검색

`GET /v1/games/{game_id}/materials`

수사 상태를 기준으로 자료를 분류하고 검색한다. 상세 본문은 개별 자료 조회에서 받는다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다. 익명 수사는 `X-Game-Token`, 계정 수사는 `X-Access-Token`과 해당 계정 문맥으로 접근한다.

## 입력

경로 값: `game_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

쿼리: kind=evidence/testimony/derived, archive_kind=evidence/testimony/inference, search=검색어, place=장소 이름. 필터는 선택적이며 단순 대소문자 무시 문자열 포함 검색입니다. 잘못된 종류 문자열을 별도 enum 오류로 거절하지 않고 빈 목록이 될 수 있습니다.

## 서버 처리 순서

1. 현재 phase에 공개 가능한 원본 제목·요약을 구성합니다.
2. 기록된 진술과 생성된 추론도 같은 목록에 합칩니다.
3. kind·archive_kind·search·place로 서버에서 필터링합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

```json
{
  "materials": [
    {
      "id": "1-01",
      "kind": "evidence",
      "archiveKind": "evidence",
      "acquired": false,
      "materialKey": "evidence:1-01",
      "title": "자료 제목"
    }
  ]
}
```

## 실패·주의점

- 필터는 일반 문자열이며 알 수 없는 값은 보통 빈 목록입니다.
- 목록이 보인다고 본문을 열람한 것은 아닙니다.

처리 진입점은 `materials()`이다. [컨트롤러 소스](../../../app/investigation/controllers/investigation_material_controller.py#L17)
