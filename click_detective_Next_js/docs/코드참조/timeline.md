# 사건 타임라인

FastAPI가 정리한 시간순 기록과 근거 링크를 표시합니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## timeline-screen.tsx

[소스 보기](../../features/timeline/timeline-screen.tsx)

### TimelineScreen

```ts
export function TimelineScreen({ busy, openEvidence, state }: Props)
```

서버가 정리한 시간순 사건 기록을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.busy`: 요청 처리 중인지 여부.
- `props.openEvidence`: 자료를 열람하고 문서 팝업을 여는 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
