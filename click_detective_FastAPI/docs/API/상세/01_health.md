# 01. 서버 시작 완료 확인

[API 목차](README.md) · [공통 규칙](../공통규칙.md)

## 역할과 호출 시점

`GET /healthz`

서버 시작 완료 확인에 사용하는 실제 구현 경로입니다. 공개 상태나 파일을 조회합니다. GET은 게임 상태를 변경하지 않습니다.

## 인증

인증 없이 호출합니다.

## 입력

요청 본문은 없습니다.

## 서버 처리 순서

1. 앱 시작 절차를 마친 서버가 응답 가능한지 확인합니다. fixture에서는 모델을 로딩하지 않습니다.
2. 실제 질문 생성이나 GPU 여유 메모리를 검사하지 않습니다.

## 응답

아래는 구조를 설명하기 위해 일부 필드를 줄인 예시입니다. 생략한 배열·state가 실제 응답에서도 비어 있다는 뜻은 아닙니다.

```json
{
  "status": "ok"
}
```

## 실패·주의점

- 서비스 시작 전에 설정·데이터·모델 로딩에 실패하면 이 응답 자체를 받을 수 없습니다.

## 코드에서 따라가기

현재 API 진입점은 [app/main.py의 `health`](../../../app/main.py#L69)다.

처리 순서는 [GameService](../../코드참조/app/investigation/service.md), 저장 조건은 [Repository](../../코드참조/app/investigation/persistence/repository.md), 공개 응답은 [Presenter](../../코드참조/app/investigation/views/presentation.md)에서 확인한다.
