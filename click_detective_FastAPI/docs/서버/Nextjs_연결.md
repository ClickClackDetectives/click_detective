# Next.js 연결과 책임

[서버 목차](README.md) · [프런트엔드 문서](../../../click_detective_Next_js/docs/README.md)

화면 프로젝트는 이 저장소의 `click_detective_Next_js`다. Next.js의 서버 경로가 FastAPI를 호출하고 공개 응답을 화면에 전달한다.

| 위치 | 책임 |
|---|---|
| 브라우저 | 화면 표시와 사용자 입력 |
| Next.js 서버 | FastAPI 호출과 수사 토큰을 포함한 서버 측 연결 |
| FastAPI | 공개 조건·게임 규칙·질문 승인·대사 생성·검증·상태 저장 |

서비스 키는 FastAPI의 `CLICK_API_KEY`와 Next.js의 `CLICK_DETECTIVE_API_KEY`에 같은 값으로 설정한다. 브라우저에 전달하는 공개 환경변수에 서비스 키를 넣지 않는다.

수사 생성 후 `game_token`을 받아 해당 수사 요청에 `X-Game-Token`으로 전달한다. 변경 요청의 `expected_revision`에는 직전에 받은 최신 `state.revision`을 사용한다.

대사 결과는 `finish_reason`으로 구분한다. `stop`은 모델 생성·검증 성공, `fixed`는 고정 대사, `fallback`은 승인 원문 복구다. 화면이 대사를 받았다는 사실과 실제 모델 생성 성공 여부는 별개다.

API의 입력과 응답은 [API 목차](../API/README.md), 서버의 저장 조건은 [상태와 SQLite](상태와_SQLite_저장.md)에서 확인한다. 원본 UI 비교 등 프런트엔드 범위는 프런트엔드 문서를 따른다.
