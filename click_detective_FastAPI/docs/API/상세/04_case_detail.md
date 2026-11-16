# 04. 특정 사건의 공개 카탈로그

[API 목차](README.md) · [공통 규칙](../공통규칙.md)

## 역할과 호출 시점

`GET /v1/cases/{case_id}`

특정 사건의 공개 카탈로그에 사용하는 실제 구현 경로입니다. 공개 상태나 파일을 조회합니다. GET은 게임 상태를 변경하지 않습니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다.

## 입력

경로 값: `case_id`. 설명용 중괄호 대신 실제 값을 넣습니다.

요청 본문은 없습니다.

## 서버 처리 순서

1. case_id가 현재 배포 사건인지 검사합니다.
2. 현재 구현에서는 catalog와 같은 공개 카탈로그를 반환합니다.

## 응답

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

```json
{
  "caseId": "thirteenth-bell-v1",
  "scenarioVersion": "snapshot-...",
  "characters": []
}
```

## 실패·주의점

- 404: 현재 배포하지 않은 case_id.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

현재 API 진입점은 [app/cases/routes.py의 `case_detail`](../../../app/cases/routes.py#L47)다.

처리 순서는 [GameService](../../코드참조/app/investigation/service.md), 저장 조건은 [Repository](../../코드참조/app/investigation/repository.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/presentation.md)에서 확인한다.
