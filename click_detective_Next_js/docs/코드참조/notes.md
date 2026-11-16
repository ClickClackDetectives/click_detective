# 메모와 자동 저장

입력창의 초안과 공식 저장 상태를 구분합니다. 자동 저장 훅은 입력이 700ms 멈췄을 때 공통 요청 큐로 저장합니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## notes-screen.tsx

[소스 보기](../../features/notes/notes-screen.tsx)

### NotesScreen

```ts
export function NotesScreen({
  state,
  notes,
  setNotes,
  noteStatus,
  busy,
  updateGame,
  setNoteStatus,
}: Props)
```

메모 입력창과 저장 상태를 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.notes`: 현재 입력 중인 수사 메모.
- `props.setNotes`: 메모 입력값을 바꾸는 함수.
- `props.noteStatus`: 메모 저장 상태를 보여주는 안내 문구.
- `props.busy`: 요청 처리 중인지 여부.
- `props.updateGame`: 행동 이름과 입력을 서버에 보내고 최신 상태를 적용하는 함수.
- `props.setNoteStatus`: 메모 저장 상태 안내를 바꾸는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## use-notes-autosave.ts

[소스 보기](../../features/notes/use-notes-autosave.ts)

### useNotesAutosave

```ts
export function useNotesAutosave({ state, notes, busy, setState, setNoteStatus }: Options)
```

입력이 멈추면 저장하고, 저장하지 않은 메모가 있으면 탭 종료를 알린다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.notes`: 현재 입력 중인 수사 메모.
- `props.busy`: 요청 처리 중인지 여부.
- `props.setState`: 서버 수사 상태를 화면에 반영하는 함수.
- `props.setNoteStatus`: 메모 저장 상태 안내를 바꾸는 함수.

반환: 없음. 메모 자동 저장과 종료 안내 효과를 등록한다.

### handler

```ts
const handler = (e: BeforeUnloadEvent) =>
```

현재 화면의 키보드 또는 탭 종료 이벤트를 처리한다.

입력:

- `e`: 사용자 입력 또는 키보드 이벤트.

반환: 없음. 브라우저 이벤트와 화면 상태를 처리한다.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
