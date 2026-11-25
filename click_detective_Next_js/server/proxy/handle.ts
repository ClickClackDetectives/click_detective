import { NextRequest, NextResponse } from 'next/server';
import { ACCESS_COOKIE } from '../auth/cookies';
import { isInvestigationId } from '../../shared/auth/contract';
import { resolveTarget } from './policy';
import { readInvestigation, readInvestigationPage } from './investigations';
import { addSearchParams, readBody } from './request';
import { allowsOrigin, fetchUpstream, upstreamFailure, upstreamTarget } from './upstream';
import {
  fail,
  upstreamError,
  gameCreated,
  streamResponse,
  clearGameCookies,
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
  if (!allowsOrigin(request)) return fail('같은 사이트에서 요청하세요.', 403, 'ORIGIN_REJECTED');
  const gameId = request.cookies.get(GAME_ID_COOKIE)?.value ?? '';
  const token = request.cookies.get(GAME_TOKEN_COOKIE)?.value ?? '';
  const investigation = request.nextUrl.searchParams.get('investigation') ?? undefined;
  const target = resolveTarget(segments, request.method, investigation);
  if (!target) return fail('지원하지 않는 API 경로입니다.', 404, 'UNKNOWN_ROUTE');
  const access = target.account ? request.cookies.get(ACCESS_COOKIE)?.value : undefined;
  if (target.account && !access) {
    return fail('로그인을 하세요', 401, 'ACCESS_TOKEN_MISSING');
  }

  const upstreamRequest = upstreamTarget(target.path);
  if (upstreamRequest instanceof NextResponse) return upstreamRequest;
  addSearchParams(upstreamRequest.url, request, segments);
  let body = await readBody(request);
  if (body instanceof NextResponse) return body;
  let claimId: string | undefined;
  if (target.claim) {
    const input = JSON.parse(body!);
    if (typeof input.game_id !== 'string' || !isInvestigationId(input.game_id)) {
      return fail('연결할 수사를 확인하세요.', 400, 'INVALID_GAME');
    }
    claimId = input.game_id as string;
    body = JSON.stringify({ game_id: claimId });
  }
  const { headers } = upstreamRequest;
  if (target.account && access) headers.set('X-Access-Token', access);
  if (claimId === gameId && token) {
    headers.set('X-Game-Token', token);
  }
  const expectedUser = request.nextUrl.searchParams.get('account');
  if (target.account && expectedUser && isInvestigationId(expectedUser)) {
    headers.set('X-Expected-User-Id', expectedUser);
  }
  const range = request.headers.get('range');
  if (range !== null) headers.set('Range', range);
  try {
    if (target.latest) {
      upstreamRequest.url.searchParams.set('limit', '1');
      const list = await fetchUpstream(upstreamRequest, 'GET');
      if (!list.ok) return await upstreamError(list);
      const page = readInvestigationPage(await list.json().catch(() => null));
      if (!page) return fail('수사 목록 응답 형식이 올바르지 않습니다.', 502, 'INVALID_RESPONSE');
      const current = page.items[0];
      if (!current) {
        return NextResponse.json({ state: null }, { headers: { 'Cache-Control': 'no-store' } });
      }
      upstreamRequest.url.pathname = '/v1/games/' + current.game_id;
      upstreamRequest.url.search = '';
    }
    const upstream = await fetchUpstream(upstreamRequest, request.method, body);
    if (!upstream.ok) return await upstreamError(upstream);
    if (target.start) return await gameCreated(upstream);
    if (claimId) {
      const data = readInvestigation(await upstream.json().catch(() => null));
      if (data?.game_id !== claimId) {
        return fail('수사 연결 응답 형식이 올바르지 않습니다.', 502, 'INVALID_RESPONSE');
      }
      const response = NextResponse.json(data, { headers: { 'Cache-Control': 'no-store' } });
      return claimId === gameId ? clearGameCookies(response) : response;
    }
    if (segments[0] === 'investigations') {
      const page = readInvestigationPage(await upstream.json().catch(() => null));
      if (!page) return fail('수사 목록 응답 형식이 올바르지 않습니다.', 502, 'INVALID_RESPONSE');
      return NextResponse.json(page, { headers: { 'Cache-Control': 'no-store' } });
    }
    return streamResponse(upstream);
  } catch (error) {
    return upstreamFailure(error);
  }
}
