# 고발과 결과

고발 폼과 결과 화면을 제공합니다. 준비도·점수·발견 여부는 서버 결과를 읽습니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## accusation-screen.tsx

[소스 보기](../../features/accusation/accusation-screen.tsx)

### AccusationScreen

```ts
export function AccusationScreen({ state, form, setForm, setModal, busy, navigateTo }: Props)
```

미종결 수사라면 준비도와 무관하게 고발 폼을 열고 근거는 선택 사항으로 받습니다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.form`: 고발 대상·동기·방법·근거 입력.
- `props.setForm`: 고발 입력값을 바꾸는 함수.
- `props.setModal`: 안내 팝업을 열거나 닫는 함수.
- `props.busy`: 요청 처리 중인지 여부.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## requirements.ts

[소스 보기](../../features/accusation/requirements.ts)

### installAccusation

```ts
export function installAccusation(minimum: number)
```

고발 준비도에 표시할 서버 기준을 보관한다.

입력:

- `minimum`: 서버가 알려준 고발 준비 표시 기준.

반환: 없음. 서버의 고발 표시 기준을 저장한다.

### getRequiredInferenceIds

```ts
export function getRequiredInferenceIds(state: GameState)
```

필수 ID는 실제 획득한 추론에 한해서 서버가 표시용으로 공개합니다.

입력:

- `state`: 서버에서 확인한 현재 수사 상태.

반환: 고발 근거에 필요한 확보 추론의 ID 목록.

### getAccusationReadiness

```ts
export function getAccusationReadiness(state: GameState)
```

서버가 알려준 고발 준비 상태를 읽는다.

입력:

- `state`: 서버에서 확인한 현재 수사 상태.

반환: 서버가 계산한 고발 준비도와 안내 정보.

## results-screen.tsx

[소스 보기](../../features/accusation/results-screen.tsx)

### ResultsScreen

```ts
export function ResultsScreen({ state, setModal, navigateTo }: Props)
```

고발 결과와 발견·미발견 항목을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.setModal`: 안내 팝업을 열거나 닫는 함수.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

### DiscoveryGroup

```ts
function DiscoveryGroup({ title, items }: { title: string; items: ReviewItem[] })
```

결과 항목을 발견 여부에 따라 나누어 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.title`: 발견 목록 위에 표시할 제목.
- `props.items`: 발견 여부를 나누어 표시할 항목 목록.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
