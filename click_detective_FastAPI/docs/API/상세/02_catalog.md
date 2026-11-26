# 02. 초기 화면용 공개 데이터

`GET /v1/catalog`

초기 화면을 만들 때 필요한 사건 소개, 인물, 공개 타임라인과 화면 설정을 한 번에 받는다.

[API 목차](README.md) · [인증·재시도 공통 규칙](../공통규칙.md)

## 접근 조건

서버 간 Bearer 서비스 키를 보낸다.

## 입력

요청 본문은 없습니다.

## 서버 처리 순서

1. `CatalogService.public_catalog()`로 명시적 공개 필드만 구성합니다.
2. 인물 portrait와 openingVideo는 FastAPI 자산 경로입니다.
3. application은 예정 사건 콘텐츠를 포함할 수 있으므로 실제 시작 여부는 cases를 확인합니다.

## 응답

응답에서 주로 쓰는 필드를 발췌한 예시다.

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

처리 진입점은 `catalog()`이다. [컨트롤러 소스](../../../app/cases/controllers/cases_controller.py#L18)
