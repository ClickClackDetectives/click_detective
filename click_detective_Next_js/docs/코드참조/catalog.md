# 사건 자료와 시작 화면

사건 소개·인물·선택지는 FastAPI 카탈로그에서 받습니다. 설치 함수는 받은 공개 자료를 화면에서 읽기 좋게 보관합니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## briefing-screen.tsx

[소스 보기](../../features/catalog/briefing-screen.tsx)

### BriefingScreen

```ts
export function BriefingScreen({ state, navigateTo }: Props)
```

사건 개요와 오프닝 재생 버튼을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## case-library.ts

[소스 보기](../../features/catalog/case-library.ts)

### installLibrary

```ts
export function installLibrary(cases: LibraryCase[])
```

사건 기록실에 표시할 카드 목록을 보관한다.

입력:

- `cases`: 서버에서 받은 사건 카드 목록.

반환: 없음. 사건 선택 자료를 갱신한다.

## case-opening.tsx

[소스 보기](../../features/catalog/case-opening.tsx)

### CaseOpening

```ts
export function CaseOpening({ gameId }: { gameId: string })
```

오프닝 영상 팝업과 재생 버튼을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.gameId`: 현재 수사의 ID.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

### keys

```ts
function keys(event: KeyboardEvent)
```

오프닝 팝업의 키보드 이동을 처리한다.

입력:

- `event`: 브라우저 이벤트.

반환: 없음. Escape 닫기와 Tab 초점 이동을 처리한다.

### play

```ts
async function play()
```

오프닝 영상을 처음부터 재생한다.

입력: 없음.

반환: 영상 재생을 시도하고 차단 안내를 적용하면 완료되는 Promise.

## cases-screen.tsx

[소스 보기](../../features/catalog/cases-screen.tsx)

### CasesScreen

```ts
export function CasesScreen({ busy, ready, inProgress, startInvestigation, setModal }: Props)
```

사건 카드와 준비 중 사건 안내를 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.busy`: 요청 처리 중인지 여부.
- `props.ready`: 최초 수사 복원 요청이 끝났는지 여부.
- `props.inProgress`: 진행 중인 수사가 있으면 해당 상태, 없으면 null 또는 false.
- `props.startInvestigation`: 기존 수사를 이어가거나 새 수사를 만드는 함수.
- `props.setModal`: 안내 팝업을 열거나 닫는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## catalog.ts

[소스 보기](../../features/catalog/catalog.ts)

### installCatalog

```ts
export function installCatalog(data: PublicCatalog)
```

브라우저가 초기 카탈로그를 받은 후 원본 화면의 읽기 전용 표시 자료를 준비합니다.

입력:

- `data`: 서버에서 받은 공개 자료.

반환: 없음. 카탈로그 표시 자료를 갱신한다.

## home-screen.tsx

[소스 보기](../../features/catalog/home-screen.tsx)

### HomeScreen

```ts
export function HomeScreen({ busy, ready, inProgress, startInvestigation, navigateTo }: Props)
```

시작·이어하기 버튼이 있는 홈 화면을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.busy`: 요청 처리 중인지 여부.
- `props.ready`: 최초 수사 복원 요청이 끝났는지 여부.
- `props.inProgress`: 진행 중인 수사가 있으면 해당 상태, 없으면 null 또는 false.
- `props.startInvestigation`: 기존 수사를 이어가거나 새 수사를 만드는 함수.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## types.ts

[소스 보기](../../features/catalog/types.ts)

타입·상수 또는 다른 구현의 재내보내기를 정의하는 파일입니다.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
