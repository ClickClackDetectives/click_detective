# 02. 초기 화면용 공개 데이터

[API 목차](README.md) · [공통 규칙](../공통규칙.md)

## 역할과 호출 시점

`GET /v1/catalog`

초기 화면용 공개 데이터에 사용하는 실제 구현 경로입니다. 공개 상태나 파일을 조회합니다. GET은 게임 상태를 변경하지 않습니다.

## 인증

`Authorization: Bearer <CLICK_API_KEY 값>`이 필요합니다.

## 입력

요청 본문은 없습니다.

## 서버 처리 순서

1. Catalog.public_catalog()로 명시적 공개 필드만 구성합니다.
2. 인물 portrait와 openingVideo는 FastAPI 자산 경로입니다.
3. application은 예정 사건 콘텐츠를 포함할 수 있으므로 실제 시작 여부는 cases를 확인합니다.

## 응답

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

```json
{
  "caseId": "thirteenth-bell-v1",
  "scenarioVersion": "snapshot-...",
  "case": {
    "title": "사건 제목"
  },
  "characters": [
    "공개 인물 객체 5개"
  ],
  "motiveOptions": [],
  "methodOptions": [],
  "publicTimeline": [],
  "questionLimit": 25,
  "briefing": [],
  "openingVideo": "/v1/assets/assets/intro/thirteenth-bell-opening-v3-quiet.mp4",
  "application": {},
  "screenLabels": {}
}
```

## 실패·주의점

- 정답·쟁점 조건·추론 조합·대본 전체를 반환하는 API가 아닙니다.
- 공통 인증 실패는 401입니다. 수사 경로에서는 권한이 없으면 404, 버전이 다르면 409가 날 수 있습니다.

## 코드에서 따라가기

현재 API 진입점은 [app/cases/routes.py의 `catalog`](../../../app/cases/routes.py#L12)다.

처리 순서는 [GameService](../../코드참조/app/investigation/service.md), 저장 조건은 [수사 저장](../../서버/수사_저장.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/views/presentation.md)에서 확인한다.
