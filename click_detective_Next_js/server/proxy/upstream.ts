import type { NextRequest } from 'next/server';
import { isSameOrigin } from './policy';
import { backendTimeout } from './request';
import { fail } from './responses';

/** 변경 요청의 Origin이 현재 사이트의 출처인지 확인한다.
 * @param request 검증할 브라우저 요청.
 * @returns 조회이거나 같은 출처인 요청이면 true.
 */
export function allowsOrigin(request: NextRequest) {
  const siteUrl =
    request.nextUrl.protocol + '//' + (request.headers.get('host') || request.nextUrl.host);
  return request.method === 'GET' || isSameOrigin(siteUrl, request.headers.get('origin'));
}

/** 서버 환경변수로부터 백엔드 주소와 내부 전용 헤더를 준비한다.
 * @param path 허용 목록에서 선택한 내부 API 경로.
 * @returns 주소·헤더 또는 설정 오류 응답.
 */
export function upstreamTarget(path: string) {
  const base = process.env.CLICK_DETECTIVE_API_URL;
  const key = process.env.CLICK_DETECTIVE_API_KEY;
  if (!base || !key) return fail('Next.js 서버 환경변수를 확인하세요.', 503, 'SERVER_CONFIG');
  try {
    const url = new URL(path, base);
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) {
      throw new Error('백엔드 주소 형식 오류');
    }
    const headers = new Headers({
      Authorization: 'Bearer ' + key,
      'Content-Type': 'application/json',
    });
    return { url, headers };
  } catch {
    return fail('백엔드 주소 설정을 확인하세요.', 503, 'SERVER_CONFIG');
  }
}

/** 서버에서 정해진 백엔드만 호출한다.
 * @param target 내부 주소와 서비스 인증 헤더.
 * @param method 허용 목록에서 확인한 HTTP 메서드.
 * @param body 검증한 요청 본문. 조회 시에는 생략한다.
 * @returns 재시도 없이 한 번 호출한 응답을 기다리는 Promise.
 */
export function fetchUpstream(
  target: { url: URL; headers: Headers },
  method: string,
  body?: string,
) {
  return fetch(target.url, {
    method,
    headers: target.headers,
    body,
    cache: 'no-store',
    signal: AbortSignal.timeout(backendTimeout()),
    redirect: 'error',
  });
}

/** 네트워크 실패를 사용자가 확인할 수 있는 오류로 바꾼다.
 * @param error 백엔드 요청 중 발생한 예외.
 * @returns 연결 또는 시간 초과 오류 응답.
 */
export function upstreamFailure(error: unknown) {
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
