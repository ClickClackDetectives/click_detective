# 03. 실제 시작 가능한 사건 목록

`GET /v1/cases`

현재 서버에서 수사를 시작할 수 있는 사건과 각 사건의 버전을 확인한다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다.

## 입력

요청 본문은 없습니다.

## 서버 처리 순서

1. Catalog에 실제 배포된 사건 한 개를 반환합니다.
2. 응답의 case_id·scenario_version을 새 수사에 사용합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

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

처리 진입점은 `cases()`이다. [컨트롤러 소스](../../../app/cases/controllers/cases_controller.py#L31)
