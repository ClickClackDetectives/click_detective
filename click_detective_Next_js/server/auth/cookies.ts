import type { NextRequest, NextResponse } from 'next/server';

export const ACCESS_COOKIE = 'cd_access_token';
export const REFRESH_COOKIE = 'cd_refresh_token';

/** 인증 쿠키를 올바른 경로와 만료 시각으로 설정하거나 지운다.
 * @param response 쿠키를 추가할 중계 응답.
 * @param request HTTPS 여부를 결정할 브라우저 요청.
 * @param tokens 토큰과 만료 시각. 생략 시 동일 경로의 쿠키를 즉시 지운다.
 * @returns 없음. 응답의 Set-Cookie를 변경한다.
 */
export function writeAuthCookies(
  response: NextResponse,
  request: NextRequest,
  tokens?: {
    access_token: string;
    refresh_token: string;
    access_expires_at: string;
    refresh_expires_at: string;
  },
) {
  const options = {
    httpOnly: true,
    sameSite: 'lax' as const,
    secure: request.nextUrl.protocol === 'https:',
  };
  response.cookies.set(ACCESS_COOKIE, tokens?.access_token ?? '', {
    ...options,
    path: '/',
    expires: tokens ? new Date(tokens.access_expires_at) : new Date(0),
  });
  response.cookies.set(REFRESH_COOKIE, tokens?.refresh_token ?? '', {
    ...options,
    path: '/api/auth',
    expires: tokens ? new Date(tokens.refresh_expires_at) : new Date(0),
  });
}
