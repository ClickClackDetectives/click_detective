# 앱 조립과 공통 화면

`CaseApp`이 공통 UI와 현재 화면을 조립하고, `InvestigationWorkspace`가 수사 화면을 배치합니다. 상태와 요청 함수는 `useCaseGame`에서 전달받습니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## app-header.tsx

[소스 보기](../../features/application/app-header.tsx)

### AppHeader

```ts
export function AppHeader({ view, state, inProgress, navigateTo, setModal }: Props)
```

현재 화면에 맞는 상단 메뉴를 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.view`: 현재 선택한 화면 이름.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.inProgress`: 진행 중인 수사가 있으면 해당 상태, 없으면 null 또는 false.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.
- `props.setModal`: 안내 팝업을 열거나 닫는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## case-app.tsx

[소스 보기](../../features/application/case-app.tsx)

### CaseApp

```ts
export default function CaseApp()
```

앱의 조립도: 상태를 가져와 현재 화면과 공통 UI에 전달한다.

입력: 없음.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## game-dialog.tsx

[소스 보기](../../features/application/game-dialog.tsx)

### GameDialog

```ts
export function GameDialog({
  modal,
  busy,
  setModal,
  updateGame,
  form,
  navigateTo,
  startInvestigation,
}: Props)
```

고발 확인·수사 초기화·도움말 팝업을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.modal`: 열린 안내 팝업 이름.
- `props.busy`: 요청 처리 중인지 여부.
- `props.setModal`: 안내 팝업을 열거나 닫는 함수.
- `props.updateGame`: 행동 이름과 입력을 서버에 보내고 최신 상태를 적용하는 함수.
- `props.form`: 고발 대상·동기·방법·근거 입력.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.
- `props.startInvestigation`: 기존 수사를 이어가거나 새 수사를 만드는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## investigation-sidebar.tsx

[소스 보기](../../features/application/investigation-sidebar.tsx)

### InvestigationSidebar

```ts
export function InvestigationSidebar({ view, state, mobile, navigateTo }: Props)
```

수사 메뉴와 진행 현황을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.view`: 현재 선택한 화면 이름.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.mobile`: 모바일 수사 메뉴가 열려 있는지 여부.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## investigation-workspace.tsx

[소스 보기](../../features/application/investigation-workspace.tsx)

### InvestigationWorkspace

```ts
export function InvestigationWorkspace({ controller }: { controller: CaseGameController })
```

수사 메뉴와 현재 선택한 작업 화면을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.controller`: 화면 상태와 사용자 행동 함수 묶음.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## navigation.ts

[소스 보기](../../features/application/navigation.ts)

타입·상수 또는 다른 구현의 재내보내기를 정의하는 파일입니다.

## original-app-loader.tsx

[소스 보기](../../features/application/original-app-loader.tsx)

### OriginalAppLoader

```ts
export function OriginalAppLoader()
```

사건 자료를 서버에서 준비한 다음 원본 UI를 그대로 실행합니다.

입력: 없음.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
