import { NextRequest, NextResponse } from 'next/server';
import { isInvestigationId } from '../../shared/auth/contract';
import { SIGNUP_PASSWORD_HINT } from '../../shared/auth/password';
import { fail } from '../proxy/responses';
import { readBody } from '../proxy/request';
import { allowsOrigin, fetchUpstream, upstreamFailure, upstreamTarget } from '../proxy/upstream';
import { ACCESS_COOKIE, REFRESH_COOKIE, writeAuthCookies } from './cookies';
import { readPublicUser, readTokenPair, resolveAuthTarget } from './contract';

const messages: Record<string, string> = {
  ACCESS_TOKEN_MISSING: '로그인이 필요합니다.',
  ACCESS_TOKEN_EXPIRED: '접근 시간이 만료되었습니다.',
  ACCESS_TOKEN_INVALID: '다시 로그인하세요.',
  SESSION_REVOKED: '세션이 종료되었습니다. 다시 로그인하세요.',
  REFRESH_TOKEN_INVALID: '다시 로그인하세요.',
  SERVICE_AUTH_REQUIRED: '서버 연결 설정을 확인하세요.',
  LOGIN_FAILED: '이메일 또는 비밀번호를 확인하세요.',
  EMAIL_EXISTS: '이미 가입된 이메일입니다.',
  AUTH_DISABLED: '현재 계정 기능을 사용할 수 없습니다.',
  ACCOUNT_CHANGED: '로그인 계정이 변경되었습니다.',
  AUTH_RATE_LIMITED: '인증 요청이 너무 많습니다. 잠시 후 다시 시도하세요.',
  INVALID_EMAIL: '이메일 주소를 확인하세요.',
  INVALID_PASSWORD: SIGNUP_PASSWORD_HINT,
  AUTH_UNAVAILABLE: '계정 서버에 연결할 수 없습니다.',
};

/** 민감한 입력이나 내부 오류를 담을 수 있는 인증 오류를 공개 응답으로 변환한다.
 * @param status 백엔드 HTTP 상태 코드.
 * @param data 백엔드 오류 응답.
 * @returns 허용된 오류 코드와 필드 정보만 담은 응답.
 */
function authError(status: number, data: { detail?: unknown }) {
  const detail = data?.detail;
  if (Array.isArray(detail) && status === 422) {
    const fields: Record<string, string> = {};
    for (const entry of detail) {
      const field = entry?.loc?.[1];
      if (field === 'email') fields.email = '이메일 형식을 확인하세요.';
      if (field === 'password') fields.password = '비밀번호 정책을 확인하세요.';
    }
    return NextResponse.json(
      { error: '입력 항목을 확인하세요.', code: 'INVALID_FIELDS', fields },
      { status, headers: { 'Cache-Control': 'no-store' } },
    );
  }
  let code = 'BACKEND_' + status;
  if (detail && typeof detail === 'object' && 'code' in detail) {
    const candidate = detail.code;
    if (typeof candidate === 'string' && Object.hasOwn(messages, candidate)) code = candidate;
  }
  if (['INVALID_EMAIL', 'INVALID_PASSWORD', 'EMAIL_EXISTS'].includes(code)) {
    const field = code === 'INVALID_PASSWORD' ? 'password' : 'email';
    return NextResponse.json(
      { error: messages[code], code, fields: { [field]: messages[code] } },
      { status, headers: { 'Cache-Control': 'no-store' } },
    );
  }
  return fail(messages[code] ?? '인증 요청에 실패했습니다.', status, code);
}

/** 인증 요청을 중계하고 검증된 토큰은 쿠키에만 기록한다.
 * @param request 브라우저 인증 요청.
 * @param context Next.js가 전달한 인증 경로.
 * @returns 공개 계정·성공 또는 오류만 담은 응답.
 */
export async function handleAuth(
  request: NextRequest,
  context: { params: Promise<{ operation: string }> },
) {
  const { operation } = await context.params;
  const path = resolveAuthTarget(operation, request.method);
  if (!path) return fail('지원하지 않는 인증 경로입니다.', 404, 'UNKNOWN_ROUTE');
  if (!allowsOrigin(request)) return fail('같은 사이트에서 요청하세요.', 403, 'ORIGIN_REJECTED');

  const target = upstreamTarget(path);
  if (target instanceof NextResponse) return target;
  let body: string | undefined;
  if (operation === 'signup' || operation === 'login') {
    const input = await readBody(request);
    if (input instanceof NextResponse) return input;
    const { email, password } = JSON.parse(input!);
    body = JSON.stringify({ email, password });
  } else if (operation === 'me') {
    const access = request.cookies.get(ACCESS_COOKIE)?.value;
    if (access) target.headers.set('X-Access-Token', access);
  } else {
    const refresh = request.cookies.get(REFRESH_COOKIE)?.value;
    if (refresh) target.headers.set('X-Refresh-Token', refresh);
    if (operation === 'logout') {
      const access = request.cookies.get(ACCESS_COOKIE)?.value;
      if (access) target.headers.set('X-Access-Token', access);
    }
  }

  const expected = request.nextUrl.searchParams.get('account');
  if (expected !== null && ['me', 'refresh', 'logout'].includes(operation)) {
    if (!isInvestigationId(expected)) {
      return fail('계정 식별자를 확인하세요.', 400, 'INVALID_ACCOUNT');
    }
    target.headers.set('X-Expected-User-Id', expected);
  }
  let upstream: Response;
  try {
    upstream = await fetchUpstream(target, request.method, body);
  } catch (error) {
    return upstreamFailure(error);
  }
  const data = await upstream.json().catch(() => null);
  if (!upstream.ok) return authError(upstream.status, data);
  const options = { status: upstream.status, headers: { 'Cache-Control': 'no-store' } };
  if (operation === 'login' || operation === 'refresh') {
    const tokens = readTokenPair(data);
    if (!tokens) return fail('인증 응답 형식이 올바르지 않습니다.', 502, 'INVALID_RESPONSE');
    const response = NextResponse.json({ user: tokens.user }, options);
    writeAuthCookies(response, request, tokens);
    return response;
  }
  if (operation === 'logout' && data?.ok === true) {
    const response = NextResponse.json({ ok: true }, options);
    writeAuthCookies(response, request);
    return response;
  }
  if (operation !== 'logout') {
    const user = readPublicUser(data);
    if (user) return NextResponse.json({ user }, options);
  }
  return fail('인증 응답 형식이 올바르지 않습니다.', 502, 'INVALID_RESPONSE');
}
