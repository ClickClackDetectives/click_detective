import { ApiError } from '../api/error.ts';
import type { PublicUser } from './contract.ts';

export const refreshable = new Set(['ACCESS_TOKEN_MISSING', 'ACCESS_TOKEN_EXPIRED']);
const ended = new Set([
  ...refreshable,
  'ACCESS_TOKEN_INVALID',
  'SESSION_REVOKED',
  'REFRESH_TOKEN_INVALID',
  'ACCOUNT_CHANGED',
]);
const refreshRequests = new Map<string, Promise<PublicUser | null>>();

/** 인증 요청을 같은 출처의 중계로 보낸다.
 * @param operation 실행할 인증 기능.
 * @param input 로그인 또는 회원가입 입력.
 * @param expectedUser 요청을 시작한 화면의 현재 계정.
 * @returns 공개 계정 또는 처리 결과.
 */
export async function authRequest<T>(
  operation: 'signup' | 'login' | 'me' | 'refresh' | 'logout',
  input?: { email: string; password: string },
  expectedUser?: string,
): Promise<T> {
  let path = '/api/auth/' + operation;
  if (expectedUser) path += '?account=' + encodeURIComponent(expectedUser);
  const response = await fetch(path, {
    method: operation === 'me' ? 'GET' : 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: input ? JSON.stringify(input) : undefined,
    cache: 'no-store',
  });
  const data = await response.json();
  if (!response.ok) {
    throw new ApiError(
      data.error || '인증 요청에 실패했습니다.',
      response.status,
      data.code || 'UNKNOWN',
      data.fields,
    );
  }
  return data as T;
}

/** 활성 쿠키가 가리키는 공개 계정을 확인한다.
 * @param expectedUser 요청이 적용되는 기존 계정 ID.
 * @returns 서버에서 확인한 공개 계정.
 */
async function currentUser(expectedUser?: string) {
  return (await authRequest<{ user: PublicUser }>('me', undefined, expectedUser)).user;
}

/** 같은 출처의 인증 쿠키 변경을 탭 간에 직렬화한다.
 * @param operation 잠금을 획득한 다음 실행할 인증 요청.
 * @returns 인증 요청의 결과를 기다리는 Promise.
 */
export async function withAuthLock<T>(operation: () => Promise<T>) {
  if (typeof navigator === 'undefined' || !navigator.locks) return operation();
  return navigator.locks.request('click-detective-auth-cookies', operation);
}

/** 쿠키가 교체된 경우를 먼저 확인하고 필요하면 한 번만 갱신한다.
 * @param expectedUser 갱신 요청이 적용되는 기존 계정 ID.
 * @returns 현재 공개 계정 또는 재로그인이 필요한 경우 null.
 */
async function restoreUser(expectedUser?: string) {
  try {
    return await currentUser(expectedUser);
  } catch (error) {
    if (error instanceof ApiError && ended.has(error.code) && !refreshable.has(error.code))
      return null;
    if (!(error instanceof ApiError) || !refreshable.has(error.code)) throw error;
  }
  try {
    return (await authRequest<{ user: PublicUser }>('refresh', undefined, expectedUser)).user;
  } catch (error) {
    // 요청 결과가 유실됐거나 다른 탭에서 쿠키를 바꾼 경우의 계정만 재확인한다.
    try {
      return await currentUser(expectedUser);
    } catch {
      if (error instanceof ApiError && ended.has(error.code)) return null;
      throw error;
    }
  }
}

/** 탭과 브라우저의 동시 갱신을 조정하며 공개 계정을 복원한다.
 * @param expectedUser 갱신 전에 사용 중인 계정 ID. 최초 확인에는 생략한다.
 * @returns 로그인 계정 또는 익명 상태를 기다리는 Promise.
 */
export function restoreSession(expectedUser?: string) {
  const key = expectedUser ?? '';
  const pending = refreshRequests.get(key);
  if (pending) return pending;
  const request = withAuthLock(() => restoreUser(expectedUser)).finally(() => {
    refreshRequests.delete(key);
  });
  refreshRequests.set(key, request);
  return request;
}

/** 만료 또는 계정이 바뀐 요청을 구분한다.
 * @param error 브라우저에서 받은 API 오류.
 * @returns 재로그인이 필요한 오류면 true.
 */
export function hasSessionEnded(error: unknown) {
  return error instanceof ApiError && ended.has(error.code);
}
