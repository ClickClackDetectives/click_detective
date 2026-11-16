# 증언 기록

목록·인물별 묶음·개별 진술을 나눴습니다. `matchesSection`은 화면 분류만 확인하며, 증언 획득 판정은 서버가 합니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## sections.ts

[소스 보기](../../features/testimony/sections.ts)

### matchesSection

```ts
export function matchesSection(item: AcquiredStatement, section: string)
```

선택한 증언 분류에 해당하는지 확인한다.

입력:

- `item`: 확인할 자료 또는 진술.
- `section`: 선택한 증언 분류.

반환: 진술이 선택한 분류에 속하면 true.

## statement-entry.tsx

[소스 보기](../../features/testimony/statement-entry.tsx)

### StatementEntry

```ts
export function StatementEntry({ state, item, openEvidence, navigateTo }: Props)
```

획득한 진술과 수정 이력, 출처, 타임라인 이동을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.item`: 확인할 자료 또는 진술.
- `props.openEvidence`: 자료를 열람하고 문서 팝업을 여는 함수.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## testimonies-screen.tsx

[소스 보기](../../features/testimony/testimonies-screen.tsx)

### TestimoniesScreen

```ts
export function TestimoniesScreen({ state, busy, openEvidence, navigateTo }: Props)
```

인물과 분류에 맞는 진술·심문 기록을 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.busy`: 요청 처리 중인지 여부.
- `props.openEvidence`: 자료를 열람하고 문서 팝업을 여는 함수.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

## witness-section.tsx

[소스 보기](../../features/testimony/witness-section.tsx)

### WitnessSection

```ts
export function WitnessSection({ state, w, section, busy, openEvidence, navigateTo }: Props)
```

한 인물의 최초 진술, 확보 증언과 심문 대화를 표시한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.w`: 한 인물의 서버 조회 결과.
- `props.section`: 선택한 증언 분류.
- `props.busy`: 요청 처리 중인지 여부.
- `props.openEvidence`: 자료를 열람하고 문서 팝업을 여는 함수.
- `props.navigateTo`: 선택한 화면으로 이동하는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
