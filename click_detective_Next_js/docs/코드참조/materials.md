# 증거와 자료 조회

목록 검색은 `useScreenView`, 본문 팝업은 `EvidenceDialog`입니다. 열람 확정과 본문 요청의 순서는 수사 훅의 `openEvidence`가 제어합니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## document-types.ts

[소스 보기](../../features/materials/document-types.ts)

타입·상수 또는 다른 구현의 재내보내기를 정의하는 파일입니다.

## evidence-dialog.tsx

[소스 보기](../../features/materials/evidence-dialog.tsx)

### EvidenceDialog

```ts
export function EvidenceDialog({ selectedDoc, setDoc, setAttachment, navigateTo }: Props)
```

확보한 문서 본문과 이미지, 자료 제시 버튼을 팝업으로 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.selectedDoc`: 팝업에 표시할 문서 본문과 메타데이터.
- `props.setDoc`: 문서 팝업을 열거나 닫는 함수.
- `props.setAttachment`: 심문에 첨부할 자료를 바꾸는 함수.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## evidence-screen.tsx

[소스 보기](../../features/materials/evidence-screen.tsx)

### EvidenceScreen

```ts
export function EvidenceScreen({
  state,
  filter,
  setFilter,
  busy,
  openEvidence,
  updateGame,
}: Props)
```

장소와 검색 조건에 맞는 증거 목록을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.filter`: 자료 검색창의 입력값.
- `props.setFilter`: 자료 검색 입력값을 바꾸는 함수.
- `props.busy`: 요청 처리 중인지 여부.
- `props.openEvidence`: 자료를 열람하고 문서 팝업을 여는 함수.
- `props.updateGame`: 행동 이름과 입력을 서버에 보내고 최신 상태를 적용하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## illustrations.ts

[소스 보기](../../features/materials/illustrations.ts)

타입·상수 또는 다른 구현의 재내보내기를 정의하는 파일입니다.

## use-screen-view.ts

[소스 보기](../../features/materials/use-screen-view.ts)

### useScreenView

```ts
export function useScreenView<T>(
  screen: string,
  state: GameState,
  query: Record<string, string>,
  initial: T,
)
```

원본 필터 UI는 유지하고 검색·분류 결과를 FastAPI에서 받아 표시합니다.

입력:

- `screen`: 검색할 화면 이름.
- `state`: 서버에서 확인한 현재 수사 상태.
- `query`: 화면에서 선택한 검색 조건.
- `initial`: 첫 응답 전 사용할 기본값.

반환: 서버의 화면 조회 결과와 오류 안내.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
