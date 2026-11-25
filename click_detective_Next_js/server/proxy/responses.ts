import { NextResponse } from 'next/server';
import { isInvestigationId } from '../../shared/auth/contract';

export const GAME_ID_COOKIE = 'cd_game_id';
export const GAME_TOKEN_COOKIE = 'cd_game_token';

/** 브라우저에 공개할 오류와 상태 코드를 만든다.
 * @param message 사용자에게 보여줄 안내.
 * @param status HTTP 상태 코드.
 * @param code 오류를 구분할 코드.
 * @returns 공개 오류 정보가 담긴 Next.js 응답.
 */
export function fail(message: string, status: number, code: string) {
  return NextResponse.json(
    { error: message, code },
    {
      status,
      headers: { 'Cache-Control': 'no-store' },
    },
  );
}

/** 백엔드 오류에서 공개 가능한 메시지와 코드를 전달한다.
 * @param upstream FastAPI에서 받은 HTTP 응답.
 * @returns 브라우저에 표시할 오류 응답.
 */
export async function upstreamError(upstream: Response) {
  const error = await upstream.json().catch(() => ({}));
  let message = '입력 형식이나 행동 조건을 확인하세요.';
  if (typeof error.detail === 'string') message = error.detail;
  let code = upstream.headers.get('X-Generation-Error');
  if (!code) {
    if (typeof error.detail?.code === 'string') code = error.detail.code;
    else if (error.detail === 'operation_in_progress') code = 'operation_in_progress';
    else code = 'BACKEND_' + upstream.status;
  }
  return fail(message, upstream.status, code ?? 'BACKEND_' + upstream.status);
}

/** 생성한 계정 수사의 공개 상태를 반환한다.
 * @param upstream FastAPI에서 받은 HTTP 응답.
 * @returns 수사 ID와 상태 또는 응답 검증 오류.
 */
export async function gameCreated(upstream: Response) {
  const data = await upstream.json().catch(() => null);
  if (
    typeof data?.game_id !== 'string' ||
    !isInvestigationId(data.game_id) ||
    data.game_token !== null ||
    data.state?.id !== data.game_id
  ) {
    return fail('백엔드 생성 응답 형식이 올바르지 않습니다.', 502, 'INVALID_RESPONSE');
  }
  return NextResponse.json(
    { game_id: data.game_id, state: data.state },
    { headers: { 'Cache-Control': 'no-store' } },
  );
}

/** 자산의 본문과 Range 관련 헤더를 그대로 중계한다.
 * @param upstream FastAPI에서 받은 HTTP 응답.
 * @returns 자산 본문과 필요한 헤더를 담은 응답.
 */
export function streamResponse(upstream: Response) {
  const headers = new Headers({
    'Cache-Control': 'private, no-store',
    'X-Content-Type-Options': 'nosniff',
  });
  for (const name of [
    'content-type',
    'content-length',
    'content-range',
    'accept-ranges',
    'etag',
    'last-modified',
  ]) {
    const value = upstream.headers.get(name);
    if (value !== null) headers.set(name, value);
  }
  return new NextResponse(upstream.body, { status: upstream.status, headers });
}

/** 연결이 완료된 익명 수사 쿠키를 현재 브라우저에서 지운다.
 * @param response 쿠키를 지우는 헤더를 추가할 응답.
 * @returns 익명 수사 쿠키가 만료된 응답.
 */
export function clearGameCookies(response: NextResponse) {
  response.cookies.set(GAME_ID_COOKIE, '', { path: '/', maxAge: 0, httpOnly: true });
  response.cookies.set(GAME_TOKEN_COOKIE, '', { path: '/', maxAge: 0, httpOnly: true });
  return response;
}
