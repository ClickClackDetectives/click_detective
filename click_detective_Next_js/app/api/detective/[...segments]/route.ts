import { NextRequest, NextResponse } from 'next/server';
import { resolveTarget, isSameOrigin } from '@/lib/server/proxy-policy';
export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';
const ID = 'cd_game_id',
  TOKEN = 'cd_game_token';
const fail = (message: string, status: number, code: string) =>
  NextResponse.json(
    { error: message, code },
    { status, headers: { 'Cache-Control': 'no-store' } },
  );
/** 브라우저 요청을 허용된 FastAPI 경로로 중계합니다. 비밀 키와 수사 토큰은 서버에서만 사용합니다. */
async function handle(
  request: NextRequest,
  context: { params: Promise<{ segments: string[] }> },
) {
  const { segments } = await context.params;
  if (
    request.method !== 'GET' &&
    !isSameOrigin(
      `${request.nextUrl.protocol}//${request.headers.get('host') || request.nextUrl.host}`,
      request.headers.get('origin'),
    )
  )
    return fail('같은 사이트에서 요청하세요.', 403, 'ORIGIN_REJECTED');
  const gameId = request.cookies.get(ID)?.value ?? '';
  const token = request.cookies.get(TOKEN)?.value ?? '';
  const target = resolveTarget(segments, request.method, gameId);
  if (!target)
    return fail('지원하지 않는 API 경로입니다.', 404, 'UNKNOWN_ROUTE');
  if (target.game && (!gameId || !token))
    return target.state
      ? NextResponse.json(
          { state: null },
          { headers: { 'Cache-Control': 'no-store' } },
        )
      : fail('먼저 수사를 시작하세요.', 401, 'NO_GAME');
  const base = process.env.CLICK_DETECTIVE_API_URL;
  const key = process.env.CLICK_DETECTIVE_API_KEY;
  if (!base || !key)
    return fail('Next.js 서버 환경변수를 확인하세요.', 503, 'SERVER_CONFIG');
  let url: URL;
  try {
    url = new URL(target.path, base);
    if (
      !['http:', 'https:'].includes(url.protocol) ||
      url.username ||
      url.password
    )
      throw Error();
  } catch {
    return fail('백엔드 주소 설정을 확인하세요.', 503, 'SERVER_CONFIG');
  }
  if (
    (segments[0] === 'materials' && segments.length === 1) ||
    segments[0] === 'views'
  )
    for (const name of [
      'kind',
      'archive_kind',
      'search',
      'place',
      'person',
      'category',
    ]) {
      const value = request.nextUrl.searchParams.get(name);
      if (value) url.searchParams.set(name, value);
    }
  let body: string | undefined;
  if (request.method !== 'GET') {
    if (Number(request.headers.get('content-length') ?? 0) > 100000)
      return fail('입력 크기가 너무 큽니다.', 413, 'BODY_TOO_LARGE');
    try {
      body = await request.text();
      if (Buffer.byteLength(body) > 100000)
        return fail('입력 크기가 너무 큽니다.', 413, 'BODY_TOO_LARGE');
      const parsed = JSON.parse(body);
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed))
        throw Error();
    } catch {
      return fail('JSON 객체를 입력하세요.', 400, 'INVALID_JSON');
    }
  }
  const headers = new Headers({
    Authorization: `Bearer ${key}`,
    'Content-Type': 'application/json',
  });
  if (target.game) headers.set('X-Game-Token', token);
  if (request.headers.has('range'))
    headers.set('Range', request.headers.get('range')!);
  const configuredTimeout = Number(
    process.env.CLICK_DETECTIVE_TIMEOUT_MS || 120000,
  );
  const timeout = Number.isFinite(configuredTimeout)
    ? Math.min(600000, Math.max(1000, configuredTimeout))
    : 120000;
  try {
    const upstream = await fetch(url, {
      method: request.method,
      headers,
      body,
      cache: 'no-store',
      signal: AbortSignal.timeout(timeout),
      redirect: 'error',
    });
    if (!upstream.ok) {
      if (target.state && upstream.status === 404) {
        const response = NextResponse.json({
          state: null,
          sessionExpired: true,
        });
        response.cookies.delete(ID);
        response.cookies.delete(TOKEN);
        response.headers.set('Cache-Control', 'no-store');
        return response;
      }
      const error = await upstream.json().catch(() => ({}));
      const message =
        typeof error.detail === 'string'
          ? error.detail
          : '입력 형식이나 행동 조건을 확인하세요.';
      return fail(
        message,
        upstream.status,
        upstream.headers.get('X-Generation-Error') ||
          (error.detail === 'operation_in_progress'
            ? 'operation_in_progress'
            : `BACKEND_${upstream.status}`),
      );
    }
    if (target.start) {
      const data = await upstream.json();
      if (
        typeof data.game_id !== 'string' ||
        typeof data.game_token !== 'string' ||
        !data.state
      )
        return fail(
          '백엔드 생성 응답 형식이 올바르지 않습니다.',
          502,
          'INVALID_RESPONSE',
        );
      const response = NextResponse.json(
        { state: data.state },
        { headers: { 'Cache-Control': 'no-store' } },
      );
      const options = {
        httpOnly: true,
        sameSite: 'lax' as const,
        secure: request.nextUrl.protocol === 'https:',
        path: '/',
        maxAge: 604800,
      };
      response.cookies.set(ID, data.game_id, options);
      response.cookies.set(TOKEN, data.game_token, options);
      return response;
    }
    const output = new Headers({
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
    ])
      if (upstream.headers.has(name))
        output.set(name, upstream.headers.get(name)!);
    return new NextResponse(upstream.body, {
      status: upstream.status,
      headers: output,
    });
  } catch (error) {
    const timedOut =
      error instanceof Error &&
      ['TimeoutError', 'AbortError'].includes(error.name);
    return fail(
      timedOut
        ? '백엔드 응답 대기시간이 지났습니다. 같은 요청으로 다시 확인하세요.'
        : 'FastAPI에 연결할 수 없습니다. 서버 실행 상태를 확인하세요.',
      timedOut ? 504 : 502,
      timedOut ? 'BACKEND_TIMEOUT' : 'BACKEND_UNREACHABLE',
    );
  }
}
export { handle as GET, handle as POST, handle as PUT };
