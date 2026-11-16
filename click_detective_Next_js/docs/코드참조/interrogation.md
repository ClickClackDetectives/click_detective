# 용의자 심문

인물·질문 주제·첨부 자료·질문 입력·말풍선을 표시합니다. 제출 처리는 수사 훅에서 전달한 `submitQuestion`이 담당합니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## interrogation-screen.tsx

[소스 보기](../../features/interrogation/interrogation-screen.tsx)

### InterrogationScreen

```ts
export function InterrogationScreen({
  state,
  suspect,
  setSuspect,
  currentSuspect,
  busy,
  scrollEnd,
  attachment,
  setAttachment,
  question,
  setQuestion,
  topicId,
  setTopicId,
  submitQuestion,
}: Props)
```

심문할 인물·질문·첨부 자료와 대화 기록을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.suspect`: 현재 심문할 인물 ID.
- `props.setSuspect`: 심문할 인물을 바꾸는 함수.
- `props.currentSuspect`: 현재 심문 대상으로 선택한 인물.
- `props.busy`: 요청 처리 중인지 여부.
- `props.scrollEnd`: 마지막 말풍선 위치를 가리키는 참조.
- `props.attachment`: 심문에 첨부한 자료의 ID.
- `props.setAttachment`: 심문에 첨부할 자료를 바꾸는 함수.
- `props.question`: 현재 질문 입력값.
- `props.setQuestion`: 질문 입력값을 바꾸는 함수.
- `props.topicId`: 선택한 질문 주제 ID.
- `props.setTopicId`: 선택한 질문 주제를 바꾸는 함수.
- `props.submitQuestion`: 질문을 제출하고 성공하면 입력을 비우는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## topics.ts

[소스 보기](../../features/interrogation/topics.ts)

### getInterviewTopics

```ts
export function getInterviewTopics(speaker: SuspectId)
```

백엔드가 공개한 질문 주제만 원본 버튼으로 표시합니다.

입력:

- `speaker`: 질문 주제를 조회할 인물 ID.

반환: 선택한 인물의 공개 질문 주제 목록. 인물이 없으면 빈 배열.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
