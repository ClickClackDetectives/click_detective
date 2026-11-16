import { NextRequest, NextResponse } from 'next/server';
import { resolveTarget, isSameOrigin } from './policy';
import { addSearchParams, readBody, backendTimeout } from './request';
import {
  fail,
  upstreamError,
  gameCreated,
  streamResponse,
  GAME_ID_COOKIE,
  GAME_TOKEN_COOKIE,
} from './responses';

/** 브라우저 요청을 검사한 뒤 허용된 FastAPI 기능으로 전달한다.
 * @param request 확인하거나 전달할 요청.
 * @param context Next.js가 전달한 비동기 경로 파라미터.
 * @returns 인증·경로·본문을 검사한 중계 응답.
 */
export async function handle(
  request: NextRequest,
  context: { params: Promise<{ segments: string[] }> },
) {
  const { segments } = await context.params;
  const siteUrl =
    request.nextUrl.protocol + '//' + (request.headers.get('host') || request.nextUrl.host);
  if (request.method !== 'GET' && !isSameOrigin(siteUrl, request.headers.get('origin'))) {
    return fail('같은 사이트에서 요청하세요.', 403, 'ORIGIN_REJECTED');
  }
  const gameId = request.cookies.get(GAME_ID_COOKIE)?.value ?? '';
  const token = request.cookies.get(GAME_TOKEN_COOKIE)?.value ?? '';
  const target = resolveTarget(segments, request.method, gameId);
  if (!target) return fail('지원하지 않는 API 경로입니다.', 404, 'UNKNOWN_ROUTE');
  if (target.game && (!gameId || !token)) {
    if (target.state) {
      return NextResponse.json({ state: null }, { headers: { 'Cache-Control': 'no-store' } });
    }
    return fail('먼저 수사를 시작하세요.', 401, 'NO_GAME');
  }
  const base = process.env.CLICK_DETECTIVE_API_URL;
  const key = process.env.CLICK_DETECTIVE_API_KEY;
  if (!base || !key) return fail('Next.js 서버 환경변수를 확인하세요.', 503, 'SERVER_CONFIG');
  let url: URL;
  try {
    url = new URL(target.path, base);
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) {
      throw new Error('백엔드 주소 형식 오류');
    }
  } catch {
    return fail('백엔드 주소 설정을 확인하세요.', 503, 'SERVER_CONFIG');
  }
  addSearchParams(url, request, segments);
  const body = await readBody(request);
  if (body instanceof NextResponse) return body;
  const headers = new Headers({
    Authorization: 'Bearer ' + key,
    'Content-Type': 'application/json',
  });
  if (target.game) headers.set('X-Game-Token', token);
  const range = request.headers.get('range');
  if (range !== null) headers.set('Range', range);
  try {
    const upstream = await fetch(url, {
      method: request.method,
      headers,
      body,
      cache: 'no-store',
      signal: AbortSignal.timeout(backendTimeout()),
      redirect: 'error',
    });
    if (!upstream.ok) return await upstreamError(upstream, target);
    if (target.start) return await gameCreated(upstream, request);
    return streamResponse(upstream);
  } catch (error) {
    const timedOut = error instanceof Error && ['TimeoutError', 'AbortError'].includes(error.name);
    if (timedOut) {
      return fail(
        '백엔드 응답 대기시간이 지났습니다. 같은 요청으로 다시 확인하세요.',
        504,
        'BACKEND_TIMEOUT',
      );
    }
    return fail(
      'FastAPI에 연결할 수 없습니다. 서버 실행 상태를 확인하세요.',
      502,
      'BACKEND_UNREACHABLE',
    );
  }
}
