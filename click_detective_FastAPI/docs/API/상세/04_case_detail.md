# 04. 특정 사건의 공개 카탈로그

`GET /v1/cases/{case_id}`

지정한 사건의 공개 카탈로그를 확인한다. 승인이 필요한 정보는 수사 API에서 제공한다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다.

## 입력

경로 값: `case_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

## 서버 처리 순서

1. case_id가 현재 배포 사건인지 검사합니다.
2. 현재 구현에서는 catalog와 같은 공개 카탈로그를 반환합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

```json
{
  "caseId": "thirteenth-bell-v1",
  "scenarioVersion": "snapshot-...",
  "characters": []
}
```

## 실패·주의점

- 404: 현재 배포하지 않은 case_id.

처리 진입점은 `case_detail()`이다. [컨트롤러 소스](../../../app/cases/controllers/cases_controller.py#L44)
