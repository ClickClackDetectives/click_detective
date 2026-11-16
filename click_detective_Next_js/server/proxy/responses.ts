import { NextRequest, NextResponse } from 'next/server';
import type { Target } from './policy';

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

/** 만료된 수사는 쿠키를 지우고, 나머지 오류는 공개 가능한 내용만 전달한다.
 * @param upstream FastAPI에서 받은 HTTP 응답.
 * @param target 허용 목록에서 선택한 백엔드 경로.
 * @returns 수사 만료 또는 백엔드 오류를 공개 형식으로 바꾼 응답.
 */
export async function upstreamError(upstream: Response, target: Target) {
  if (target.state && upstream.status === 404) {
    const response = NextResponse.json({ state: null, sessionExpired: true });
    response.cookies.delete(GAME_ID_COOKIE);
    response.cookies.delete(GAME_TOKEN_COOKIE);
    response.headers.set('Cache-Control', 'no-store');
    return response;
  }
  const error = await upstream.json().catch(() => ({}));
  let message = '입력 형식이나 행동 조건을 확인하세요.';
  if (typeof error.detail === 'string') message = error.detail;
  let code = upstream.headers.get('X-Generation-Error');
  if (!code) {
    if (error.detail === 'operation_in_progress') code = 'operation_in_progress';
    else code = 'BACKEND_' + upstream.status;
  }
  return fail(message, upstream.status, code);
}

/** 생성 응답의 수사 ID와 토큰은 HttpOnly 쿠키로 보관한다.
 * @param upstream FastAPI에서 받은 HTTP 응답.
 * @param request 확인하거나 전달할 요청.
 * @returns 수사 ID와 토큰을 쿠키에 보관하고 공개 상태만 담은 응답.
 */
export async function gameCreated(upstream: Response, request: NextRequest) {
  const data = await upstream.json();
  if (typeof data.game_id !== 'string' || typeof data.game_token !== 'string' || !data.state) {
    return fail('백엔드 생성 응답 형식이 올바르지 않습니다.', 502, 'INVALID_RESPONSE');
  }
  const response = NextResponse.json(
    { state: data.state },
    {
      headers: { 'Cache-Control': 'no-store' },
    },
  );
  const options = {
    httpOnly: true,
    sameSite: 'lax' as const,
    secure: request.nextUrl.protocol === 'https:',
    path: '/',
    maxAge: 604800,
  };
  response.cookies.set(GAME_ID_COOKIE, data.game_id, options);
  response.cookies.set(GAME_TOKEN_COOKIE, data.game_token, options);
  return response;
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
