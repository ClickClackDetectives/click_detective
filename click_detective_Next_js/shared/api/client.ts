import { ApiError } from './error.ts';
import { restoreSession, refreshable, hasSessionEnded } from '../auth/client.ts';
import { accountApiPath, accountScope, isPublicApiPath, notifySessionEnd } from '../auth/scope.ts';
export { ApiError } from './error.ts';
/** 검증한 수사 경로에 요청하고 공개 응답을 읽는다.
 * @param path 중계에 전달할 경로.
 * @param method HTTP 메서드.
 * @param body 전송할 입력값.
 * @returns 서버가 반환한 JSON 응답.
 */
async function fetchGame<T>(path: string, method: string, body: unknown): Promise<T> {
  const response = await fetch(`/api/detective/${path}`, {
    method,
    cache: 'no-store',
    headers: { 'Content-Type': 'application/json' },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  const data = await response.json();
  if (!response.ok)
    throw new ApiError(
      data.error || '요청에 실패했습니다.',
      response.status,
      data.code || 'UNKNOWN',
    );
  return data as T;
}

/** 계정 토큰을 한 번 갱신한 뒤 같은 계정과 수사에 동일한 요청을 재전송한다.
 * @param path 호출 경로.
 * @param method HTTP 메서드.
 * @param body 전송할 요청 본문.
 * @returns 서버가 반환한 JSON 응답.
 */
export async function api<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const scope = accountScope();
  const scopedPath = accountApiPath(path, scope);
  if (isPublicApiPath(path)) return fetchGame<T>(scopedPath, method, body);
  if (!scope.userId) throw new ApiError('로그인이 필요합니다.', 401, 'ACCESS_TOKEN_MISSING');
  /** 시작할 때 확인했던 계정과 수사가 여전히 열려 있는지 확인한다.
   * @returns 범위가 그대로 유지되면 true.
   */
  function sameScope() {
    const current = accountScope();
    return current.userId === scope.userId && current.investigation === scope.investigation;
  }
  /** 보호 요청을 전송하고 해당 수사 범위가 유지된 경우에만 결과를 사용한다.
   * @returns 현재 수사 화면에 적용할 JSON 응답.
   */
  async function requestInScope() {
    if (!sameScope())
      throw new ApiError('현재 계정에서 다시 수사를 열어주세요.', 409, 'ACCOUNT_CHANGED');
    const result = await fetchGame<T>(scopedPath, method, body);
    if (!sameScope())
      throw new ApiError('현재 계정에서 다시 수사를 열어주세요.', 409, 'ACCOUNT_CHANGED');
    return result;
  }
  try {
    try {
      return await requestInScope();
    } catch (error) {
      if (!(error instanceof ApiError) || !refreshable.has(error.code) || !sameScope()) throw error;
    }
    const user = await restoreSession(scope.userId);
    if (!user || user.id !== scope.userId) {
      throw new ApiError('현재 계정에서 다시 수사를 열어주세요.', 401, 'ACCOUNT_CHANGED');
    }
    return await requestInScope();
  } catch (error) {
    if (sameScope() && hasSessionEnded(error)) notifySessionEnd();
    throw error;
  }
}
/** 백엔드가 준 자산 경로를 같은 출처 프록시 경로로 바꿉니다. 임의 외부 URL은 받지 않습니다.
 * @param path 호출 경로나 파일 경로.
 * @returns 같은 출처의 자산 프록시 경로. 허용되지 않으면 빈 문자열.
 */
export function assetUrl(path: string): string {
  if (path.startsWith('/v1/assets/'))
    return '/api/detective/assets/' + path.slice('/v1/assets/'.length);
  const match = path.match(/^\/v1\/games\/[^/]+\/evidence-assets\/([^/]+)$/);
  if (!match) return '';
  const asset = 'evidence-assets/' + encodeURIComponent(match[1]);
  return '/api/detective/' + accountApiPath(asset);
}
