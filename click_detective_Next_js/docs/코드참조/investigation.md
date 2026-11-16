# 수사 상태와 행동 요청

화면 입력과 서버 상태를 연결하는 중심입니다. `useCaseGame → updateGame → requestGame → mapGameCommand → api` 순서로 읽으면 됩니다. `game-client.ts`의 최신 상태·요청 큐·미확정 요청은 이 모듈에 보관합니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## commands.ts

[소스 보기](../../features/investigation/commands.ts)

### mapGameCommand

```ts
export function mapGameCommand(action: string, input: Record<string, unknown>)
```

화면의 기존 행동 이름을 FastAPI 계약으로 바꿉니다. 규칙을 판정하지 않습니다.

입력:

- `action`: 실행할 수사 행동 이름.
- `input`: 화면에서 받은 행동 입력.

반환: 백엔드 행동 경로와 요청 필드.

## documents.ts

[소스 보기](../../features/investigation/documents.ts)

### requestDocument

```ts
export async function requestDocument(
  id: string,
  state: GameState,
): Promise<InvestigationDocument>
```

원본 팝업의 문서 형태를 서버 상세 응답에서 만듭니다. 본문은 미리 번들에 넣지 않습니다.

입력:

- `id`: 자료 또는 수사 식별자.
- `state`: 서버에서 확인한 현재 수사 상태.

반환: 화면에 표시할 원본·진술·추론 문서.

## game-client.ts

[소스 보기](../../features/investigation/game-client.ts)

### accept

```ts
function accept(state: GameState | null)
```

응답 버전을 보관합니다. 과거 UUID의 캐시 응답으로 최신 상태를 되돌리지 않습니다.

입력:

- `state`: 서버에서 확인한 현재 수사 상태.

반환: 과거 응답으로 되돌리지 않은 최신 수사 상태.

### send

```ts
async function send(request: NonNullable<typeof pending>)
```

불확실한 통신 실패는 동일 UUID로 재확인하고 새 행동은 그 뒤에 전송합니다.

입력:

- `request`: 확인하거나 전달할 요청.

반환: 동일 요청의 결과로 확인한 수사 상태.

### requestGame

```ts
export function requestGame(action: string, body?: unknown): Promise<GameState | null>
```

원본 화면의 요청 인터페이스입니다. 자동 저장과 심문을 직렬화해 revision 충돌을 피합니다.

입력:

- `action`: 실행할 수사 행동 이름.
- `body`: 전송할 요청 본문.

반환: 서버에서 확인한 최신 수사 상태 또는 null을 기다릴 Promise.

### currentGame

```ts
export function currentGame()
```

오류 처리 후에도 화면이 서버에서 확인된 최신 저장 버전을 사용할 수 있게 합니다.

입력: 없음.

반환: 마지막으로 확인한 수사 상태 또는 null.

## progress.ts

[소스 보기](../../features/investigation/progress.ts)

### getInvestigationProgress

```ts
export function getInvestigationProgress(state: GameState)
```

진행률은 FastAPI가 계산한 값을 그대로 반환합니다.

입력:

- `state`: 서버에서 확인한 현재 수사 상태.

반환: 서버가 계산한 수사 진행률과 항목별 집계.

## stage.ts

[소스 보기](../../features/investigation/stage.ts)

### installStage

```ts
export function installStage(value: typeof secondRoundRequirements)
```

표시할 목표 개수도 백엔드 설정에서 읽습니다.

입력:

- `value`: 입력하거나 변환할 값.

반환: 없음. 서버가 알려준 단계 기준을 저장한다.

### getSecondRoundEligibility

```ts
export function getSecondRoundEligibility(state: GameState)
```

서버가 알려준 2차 조사 조건을 읽는다.

입력:

- `state`: 서버에서 확인한 현재 수사 상태.

반환: 서버가 계산한 2차 조사 가능 여부와 부족 조건.

## types.ts

[소스 보기](../../features/investigation/types.ts)

타입·상수 또는 다른 구현의 재내보내기를 정의하는 파일입니다.

## use-case-game.ts

[소스 보기](../../features/investigation/use-case-game.ts)

### useCaseGame

```ts
export function useCaseGame()
```

화면 상태와 서버 요청을 연결한다. 화면 마크업은 각 features 폴더에 있다.

입력: 없음.

반환: 수사 상태, 화면 입력값과 행동 함수 묶음.

### updateGame

```ts
async function updateGame(action: string, body: unknown)
```

버튼에서 실행하는 요청의 로딩·오류·최신 수사 상태를 공통 처리한다.

입력:

- `action`: 실행할 수사 행동 이름.
- `body`: 전송할 요청 본문.

반환: 성공하면 최신 수사 상태, 실패하거나 잠겨 있으면 null.

### navigateTo

```ts
function navigateTo(v: View)
```

선택한 화면으로 이동하고 팝업·모바일 메뉴를 정리한다.

입력:

- `v`: 이동할 화면.

반환: 없음. 화면 상태를 바꾼다.

### startInvestigation

```ts
async function startInvestigation(restart = false)
```

기존 수사를 이어가거나 새로운 수사를 만든다.

입력:

- `restart`: 현재 기록을 초기화하고 새 수사를 만들지 여부.

반환: 수사 생성·복원과 화면 이동이 끝나면 완료되는 Promise.

### openEvidence

```ts
async function openEvidence(id: string)
```

열람 확정 후 서버에서 본문을 받아 원본 문서 팝업에 표시합니다.

입력:

- `id`: 자료 또는 수사 식별자.

반환: 문서 조회·표시를 마치면 완료되는 Promise.

### submitQuestion

```ts
async function submitQuestion(e: React.FormEvent)
```

화면 입력만 전달한다. 남은 횟수와 증거 유효성의 최종 검사는 서버가 한다.

입력:

- `e`: 사용자 입력 또는 키보드 이벤트.

반환: 심문과 입력 초기화를 마치면 완료되는 Promise.

## use-dialog-effects.ts

[소스 보기](../../features/investigation/use-dialog-effects.ts)

### useMessageScroll

```ts
export function useMessageScroll(
  scrollEnd: RefObject<HTMLDivElement | null>,
  count: number | undefined,
)
```

새 대화가 생기면 마지막 메시지로 이동한다.

입력:

- `scrollEnd`: 마지막 말풍선 위치를 가리키는 참조.
- `count`: 현재 대화 개수.

반환: 없음. 대화 스크롤 효과를 등록한다.

### useDialogEffects

```ts
export function useDialogEffects(
  modal: string | null,
  doc: string | null,
  busy: boolean,
  setModal: (modal: string | null) => void,
  setDoc: (doc: string | null) => void,
  setSelectedDoc: (doc: InvestigationDocument | undefined) => void,
)
```

팝업이 열린 동안 스크롤과 키보드 초점을 관리한다.

입력:

- `modal`: 열린 안내 팝업 이름.
- `doc`: 열린 문서 ID.
- `busy`: 요청 처리 중인지 여부.
- `setModal`: 안내 팝업을 열거나 닫는 함수.
- `setDoc`: 문서 팝업을 열거나 닫는 함수.
- `setSelectedDoc`: 표시할 문서 본문을 바꾸는 함수.

반환: 없음. 팝업 키보드·스크롤 효과를 등록한다.

### handler

```ts
const handler = (e: KeyboardEvent) =>
```

현재 화면의 키보드 또는 탭 종료 이벤트를 처리한다.

입력:

- `e`: 사용자 입력 또는 키보드 이벤트.

반환: 없음. 브라우저 이벤트와 화면 상태를 처리한다.

## use-restore-game.ts

[소스 보기](../../features/investigation/use-restore-game.ts)

### useRestoreGame

```ts
export function useRestoreGame(
  setState: (state: GameState | null) => void,
  setNotes: (notes: string) => void,
  setError: (message: string) => void,
  setReady: (ready: boolean) => void,
)
```

처음 열 때 쿠키에 연결된 수사 기록을 불러온다.

입력:

- `setState`: 서버 수사 상태를 화면에 반영하는 함수.
- `setNotes`: 메모 입력값을 바꾸는 함수.
- `setError`: 화면의 오류 안내를 바꾸는 함수.
- `setReady`: 초기 자료 준비 여부를 바꾸는 함수.

반환: 없음. 초기 복원 효과를 등록한다.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
