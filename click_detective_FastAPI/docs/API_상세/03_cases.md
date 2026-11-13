# 03. 실제 시작 가능한 사건 목록

[API 목차](README.md) · [공통 규칙](../06_API_공통규칙과_전체목록.md)

## 역할과 호출 시점

`GET /v1/cases`

실제 시작 가능한 사건 목록에 사용하는 실제 구현 경로입니다. 공개 상태나 파일을 조회합니다. GET은 게임 상태를 변경하지 않습니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다.

## 입력

요청 본문은 없습니다.

## 서버 처리 순서

1. Catalog에 실제 배포된 사건 한 개를 반환합니다.
2. 응답의 case_id·scenario_version을 새 수사에 사용합니다.

## 응답

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

```json
{
  "cases": [
    {
      "case_id": "thirteenth-bell-v1",
      "scenario_version": "snapshot-...",
      "id": "사건 내부 ID",
      "title": "제목"
    }
  ]
}
```

## 실패·주의점

- 사건 선택용 예정 콘텐츠의 ID와 실제 case_id를 혼동하지 않습니다.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

[app/main.py의 cases()](../../app/main.py#L92)에서 시작합니다. 생성·변경은 [GameService](../파이썬_파일별_상세/app/service.md), 저장은 [Repository](../파이썬_파일별_상세/app/repository.md), 화면 상태는 [Presenter](../파이썬_파일별_상세/app/presentation.md)를 확인하세요.
