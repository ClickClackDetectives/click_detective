# 자료 연결과 추론

자료 선택과 연결 요청을 처리합니다. 확보 추론 카드는 `DerivedList`, 출처 표시 보조 함수는 `sources.ts`에 있습니다. 추론의 정답은 서버가 판정합니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## derived-list.tsx

[소스 보기](../../features/inference/derived-list.tsx)

### DerivedList

```ts
export function DerivedList({ state, openEvidence, title, open }: Props)
```

이미 확보한 추론 문서와 직접·원본 근거를 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.openEvidence`: 자료를 열람하고 문서 팝업을 여는 함수.
- `props.title`: 출처의 표시 제목을 만드는 함수.
- `props.open`: 선택한 출처를 여는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## inference-screen.tsx

[소스 보기](../../features/inference/inference-screen.tsx)

### InferenceScreen

```ts
export function InferenceScreen({ state, busy, updateGame, openEvidence, navigateTo }: Props)
```

연결할 자료 선택과 확보한 추론을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.busy`: 요청 처리 중인지 여부.
- `props.updateGame`: 행동 이름과 입력을 서버에 보내고 최신 상태를 적용하는 함수.
- `props.openEvidence`: 자료를 열람하고 문서 팝업을 여는 함수.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

### title

```ts
function title(ref: SourceRef)
```

출처의 화면용 제목을 만든다.

입력:

- `ref`: 자료 종류와 ID가 담긴 출처.

반환: 출처의 화면용 제목 문자열.

### open

```ts
function open(ref: SourceRef)
```

선택한 출처의 자료를 연다.

입력:

- `ref`: 자료 종류와 ID가 담긴 출처.

반환: 없음. 선택한 자료를 여는 비동기 작업을 시작한다.

### toggle

```ts
function toggle(ref: SourceRef)
```

선택한 자료를 추가하거나 해제한다.

입력:

- `ref`: 자료 종류와 ID가 담긴 출처.

반환: 없음. 선택한 자료 목록을 바꾼다.

### connect

```ts
async function connect()
```

현재 선택한 자료로 추론 생성을 요청한다.

입력: 없음.

반환: 추론 요청과 결과 안내 처리가 끝나면 완료되는 Promise.

## sources.ts

[소스 보기](../../features/inference/sources.ts)

### describeSource

```ts
export function describeSource(state: GameState, ref: SourceRef)
```

자료 참조를 화면용 번호·제목·보충 설명으로 변환한다.

입력:

- `state`: 서버에서 확인한 현재 수사 상태.
- `ref`: 자료 종류와 ID가 담긴 출처.

반환: 자료 종류·번호·제목·설명이 담긴 표시용 출처.

### getInferenceSources

```ts
export function getInferenceSources(state: GameState)
```

실제 출처 후보도 서버에서 받은 목록을 사용합니다.

입력:

- `state`: 서버에서 확인한 현재 수사 상태.

반환: 현재 수사에서 확보한 연결 후보 목록.

### getInferenceBasisLabel

```ts
export function getInferenceBasisLabel(state: GameState, sources: SourceRef[])
```

도출 문서의 근거 종류 이름은 서버가 계산합니다.

입력:

- `state`: 서버에서 확인한 현재 수사 상태.
- `sources`: 추론을 구성한 출처 목록.

반환: 서버가 알려준 추론 근거 설명. 해당 설명이 없으면 기본 문구.

### sourceKey

```ts
export function sourceKey(ref: SourceRef)
```

자료 종류와 ID를 합쳐 목록의 식별자를 만든다.

입력:

- `ref`: 자료 종류와 ID가 담긴 출처.

반환: 자료 종류와 ID를 합친 문자열.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
