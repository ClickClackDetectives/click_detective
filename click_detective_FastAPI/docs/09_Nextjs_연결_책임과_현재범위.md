# Next.js 연결 책임과 현재 범위

새 프런트엔드 `~/reverse/click_detective_nextjs`가 연결 대상입니다. 원본 `share_project`의 화면·CSS·모바일 배치·오프닝·팝업·자동 저장 흐름을 유지하면서 자료 처리·저장을 이 FastAPI로 대체합니다. 원본 프로젝트는 수정하지 않습니다.

Next.js BFF는 API 키를 서버에 보관하고 수사 토큰을 HttpOnly 쿠키에 저장합니다. 화면은 같은 출처 /api/detective만 호출합니다. 배경·인물·노트·영상의 원래 URL은 Next.js에서 받아 인증된 FastAPI 자산으로 중계합니다.

진행률·단계·고발·출처·규칙 판정은 서버가 맡습니다. 원본의 검색·분류도 /views/{screen}에서 처리합니다. 실제 Qwen·어댑터·양자화·LangGraph는 백엔드 실행 설정에 따릅니다. 연결 검사 fixture 성공이 실제 생성 품질 검증은 아닙니다.

자세한 실행·파일·브라우저 비교 안내는 [프런트엔드 문서](../../click_detective_nextjs/docs/README.md)를 읽으세요.
