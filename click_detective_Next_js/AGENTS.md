# Next.js 작업 규칙

- 화면 렌더링과 사용자 입력은 `components/`의 기능별 폴더에서 수정한다. 화면 상태·조회 로직은 `app/game/`의 기존 모듈과 훅을 활용한다.
- FastAPI 요청은 기존 Route Handler와 서버 중계 코드를 사용한다. 서비스 키는 서버 코드에서 읽고, 수사 토큰은 기존 HttpOnly 쿠키 흐름으로 관리한다.
- 서버가 반환한 자료 공개 여부와 수사 결과를 화면에 표시한다. 검색·분류를 수정할 때는 서버 조회 조건, 화면 필터, 결과가 없을 때의 표시를 함께 확인한다.
- TypeScript와 JSX는 `.prettierrc.json`의 설정을 따른다. 규칙 테스트 대상인 함수·클래스는 기존 문서 주석 형식으로 매개변수와 반환값을 설명한다.

## 게임 서버 구조 변경과 검증

- 서버 중계 대상은 단일 FastAPI다. 내부 에이전트 검사는 기존 경로와 인증 흐름을 사용한다.
- API 계약이 바뀌면 프런트 타입, 서버 중계, 화면의 오류 및 빈 상태를 함께 확인한다. 백엔드 파일 이동에 따른 변경 여부는 실제 HTTP 계약을 기준으로 판단한다.
- `npm run format:check`, `npm run typecheck`, `npm test`를 실행한다. 서버 연결이나 수사 흐름의 변경에는 `npm run build` 후 `npm run test:integration`으로 fixture 검증을 수행한다.

## TypeScript·JavaScript JSDoc

- 선언 바로 위의 `/** ... */`에 작성한다. 요약 뒤에 인자마다 `@param 이름 설명`을 한 줄씩 적고 그 뒤에 `@returns 설명`을 적는다.
- 인자가 없으면 `@param`을 생략한다. 구조 분해 인자는 `@param props`로 전체를 설명하고 필요하면 `@param props.필드명`으로 필드를 설명한다.
- 반환값이 없으면 `@returns 반환값 없음.`을 적는다. 비동기 함수는 Promise가 이행될 때의 값을 설명한다. 클래스의 `@returns`에는 인스턴스의 역할을 적고 생성자 인자는 생성자 JSDoc의 `@param`에 적는다.
