# Next.js 서버의 FastAPI 중계

handle → policy/request → FastAPI → responses 순서입니다. 서비스 키와 수사 토큰은 서버에서 추가합니다.

## 읽는 기준

아래 코드는 현재 소스의 선언에서 본문을 제외한 것입니다. 입력과 반환 설명은 해당 함수의 JSDoc을 기준으로 정리했습니다. `Props`는 각 화면 파일에 정의된 입력 타입이며, 타입의 전체 필드는 소스 링크에서 확인합니다.

## server/proxy/handle.ts

[소스 열기](../../../server/proxy/handle.ts)

### handle

```ts
export async function handle(
  request: NextRequest,
  context: { params: Promise<{ segments: string[] }> },
)
```

역할: 브라우저 요청을 검사한 뒤 허용된 FastAPI 기능으로 전달한다.

입력:

- `request`: 확인하거나 전달할 요청.
- `context`: Next.js가 전달한 비동기 경로 파라미터.

반환: 인증·경로·본문을 검사한 중계 응답.

## server/proxy/policy.ts

[소스 열기](../../../server/proxy/policy.ts)

이 파일의 타입: `Target`.

### resolveTarget

```ts
export function resolveTarget(parts: string[], method: string, gameId: string): Target | null
```

역할: 브라우저가 임의의 URL이나 다른 게임 ID를 지정하지 못하도록 경로를 만듭니다.

입력:

- `parts`: 요청 경로를 나눈 문자열 목록.
- `method`: HTTP 요청 메서드.
- `gameId`: 현재 수사의 ID.

반환: 허용된 백엔드 경로. 지원하지 않으면 null.

### isSameOrigin

```ts
export function isSameOrigin(requestUrl: string, origin: string | null): boolean
```

역할: 같은 사이트의 화면에서 보낸 변경 요청만 허용합니다. Origin 없는 외부 호출도 거절합니다.

입력:

- `requestUrl`: 현재 사이트 주소.
- `origin`: 브라우저가 보낸 Origin 헤더.

반환: 변경 요청이 같은 출처이면 true.

## server/proxy/request.ts

[소스 열기](../../../server/proxy/request.ts)

### readBody

```ts
export async function readBody(request: NextRequest)
```

역할: GET을 제외한 요청의 JSON 형식과 바이트 크기를 검사한다.

입력:

- `request`: 확인하거나 전달할 요청.

반환: 정상 요청 본문, GET이면 undefined, 형식 오류면 오류 응답.

### addSearchParams

```ts
export function addSearchParams(url: URL, request: NextRequest, segments: string[])
```

역할: 허용한 검색 조건만 백엔드 주소에 추가한다.

입력:

- `url`: 요청할 서버 주소.
- `request`: 확인하거나 전달할 요청.
- `segments`: 요청 경로의 각 부분.

반환: 없음. 허용된 검색 조건을 URL에 추가한다.

### backendTimeout

```ts
export function backendTimeout()
```

역할: 환경변수의 대기 시간을 1초에서 10분 사이로 제한한다.

입력: 없음.

반환: 1초~10분 범위의 백엔드 대기 시간(ms).

## server/proxy/responses.ts

[소스 열기](../../../server/proxy/responses.ts)

### fail

```ts
export function fail(message: string, status: number, code: string)
```

역할: 브라우저에 공개할 오류와 상태 코드를 만든다.

입력:

- `message`: 사용자에게 보여줄 안내.
- `status`: HTTP 상태 코드.
- `code`: 오류를 구분할 코드.

반환: 공개 오류 정보가 담긴 Next.js 응답.

### upstreamError

```ts
export async function upstreamError(upstream: Response, target: Target)
```

역할: 만료된 수사는 쿠키를 지우고, 나머지 오류는 공개 가능한 내용만 전달한다.

입력:

- `upstream`: FastAPI에서 받은 HTTP 응답.
- `target`: 허용 목록에서 선택한 백엔드 경로.

반환: 수사 만료 또는 백엔드 오류를 공개 형식으로 바꾼 응답.

### gameCreated

```ts
export async function gameCreated(upstream: Response, request: NextRequest)
```

역할: 생성 응답의 수사 ID와 토큰은 HttpOnly 쿠키로 보관한다.

입력:

- `upstream`: FastAPI에서 받은 HTTP 응답.
- `request`: 확인하거나 전달할 요청.

반환: 수사 ID와 토큰을 쿠키에 보관하고 공개 상태만 담은 응답.

### streamResponse

```ts
export function streamResponse(upstream: Response)
```

역할: 자산의 본문과 Range 관련 헤더를 그대로 중계한다.

입력:

- `upstream`: FastAPI에서 받은 HTTP 응답.

반환: 자산 본문과 필요한 헤더를 담은 응답.

[코드 설명서 목록](../README.md) · [전체 동작 순서](../../구조/동작_순서.md)
