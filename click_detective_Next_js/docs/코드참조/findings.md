# 발견한 쟁점

심문에서 서버가 확인한 쟁점을 표시합니다. 출처를 누르면 확보한 자료를 엽니다.

선언은 현재 소스에서 본문을 제외해 옮겼습니다. 타입 이름은 같은 파일 또는 import한 타입 파일에서 확인할 수 있습니다.

## findings-screen.tsx

[소스 보기](../../features/findings/findings-screen.tsx)

### key

```ts
function key(ref: SourceRef)
```

자료 종류와 ID를 합쳐 목록 식별자를 만든다.

입력:

- `ref`: 자료 종류와 ID가 담긴 출처.

반환: 자료 종류와 ID를 합친 문자열.

### FindingsScreen

```ts
export function FindingsScreen({ state, openEvidence }: Props)
```

심문에서 확인한 사실만 표시한다. 자료 연결과 추론 생성은 별도 화면에서 처리한다.

입력:

- `props`: 화면에 전달한 상태와 사용자 행동 함수.
- `props.state`: 서버에서 확인한 현재 수사 상태.
- `props.openEvidence`: 자료를 열람하고 문서 팝업을 여는 함수.

반환: 표시할 React 화면. 표시할 내용이 없으면 null.

### title

```ts
function title(ref: SourceRef)
```

출처의 화면용 제목을 만든다.

입력:

- `ref`: 자료 종류와 ID가 담긴 출처.

반환: 확보 자료의 제목. 찾지 못하면 undefined.

### open

```ts
function open(ref: SourceRef)
```

선택한 출처의 자료를 연다.

입력:

- `ref`: 자료 종류와 ID가 담긴 출처.

반환: 없음. 선택한 자료를 여는 비동기 작업을 시작한다.

[코드 설명서 목록](README.md) · [전체 동작 순서](../구조/동작_순서.md)
