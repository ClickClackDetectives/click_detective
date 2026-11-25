import type { NextRequest } from 'next/server';
import { fail } from './responses';

/** GET을 제외한 요청의 JSON 형식과 바이트 크기를 검사한다.
 * @param request 확인하거나 전달할 요청.
 * @returns 정상 요청 본문, GET이면 undefined, 형식 오류면 오류 응답.
 */
export async function readBody(request: NextRequest) {
  if (request.method === 'GET') return undefined;
  if (Number(request.headers.get('content-length') ?? 0) > 100000) {
    return fail('입력 크기가 너무 큽니다.', 413, 'BODY_TOO_LARGE');
  }
  try {
    const body = await request.text();
    if (Buffer.byteLength(body) > 100000) {
      return fail('입력 크기가 너무 큽니다.', 413, 'BODY_TOO_LARGE');
    }
    const parsed = JSON.parse(body);
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      return fail('JSON 객체를 입력하세요.', 400, 'INVALID_JSON');
    }
    return body;
  } catch {
    return fail('JSON 객체를 입력하세요.', 400, 'INVALID_JSON');
  }
}

/** 허용한 검색 조건만 백엔드 주소에 추가한다.
 * @param url 요청할 서버 주소.
 * @param request 확인하거나 전달할 요청.
 * @param segments 요청 경로의 각 부분.
 * @returns 없음. 허용된 검색 조건을 URL에 추가한다.
 */
export function addSearchParams(url: URL, request: NextRequest, segments: string[]) {
  if (segments[0] === 'investigations') {
    for (const name of ['limit', 'cursor']) {
      const value = request.nextUrl.searchParams.get(name);
      if (value) url.searchParams.set(name, value);
    }
    return;
  }
  const materialList = segments[0] === 'materials' && segments.length === 1;
  if (!materialList && segments[0] !== 'views') return;
  for (const name of ['kind', 'archive_kind', 'search', 'place', 'person', 'category']) {
    const value = request.nextUrl.searchParams.get(name);
    if (value) url.searchParams.set(name, value);
  }
}

/** 환경변수의 대기 시간을 1초에서 10분 사이로 제한한다.
 * 파라미터 없음.
 * @returns 1초~10분 범위의 백엔드 대기 시간(ms).
 */
export function backendTimeout() {
  const configured = Number(process.env.CLICK_DETECTIVE_TIMEOUT_MS || 120000);
  if (!Number.isFinite(configured)) return 120000;
  return Math.min(600000, Math.max(1000, configured));
}
