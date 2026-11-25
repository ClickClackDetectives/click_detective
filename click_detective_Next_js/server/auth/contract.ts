import type { PublicUser } from '../../shared/auth/contract.ts';

type InternalTokenPair = {
  user: PublicUser;
  access_token: string;
  refresh_token: string;
  access_expires_at: string;
  refresh_expires_at: string;
};

/** 인증 경로의 기능과 메서드가 허용 목록에 있는지 확인한다.
 * @param operation 중계할 인증 기능.
 * @param method HTTP 메서드.
 * @returns 허용된 FastAPI 인증 경로 또는 null.
 */
export function resolveAuthTarget(operation: string, method: string) {
  if (operation === 'me' && method === 'GET') return '/auth/me';
  if (method === 'POST' && ['signup', 'login', 'refresh', 'logout'].includes(operation))
    return '/auth/' + operation;
  return null;
}

/** 공개 계정 요약에서 허용한 필드만 읽는다.
 * @param value FastAPI 응답에서 읽은 계정 요약.
 * @returns 검증된 공개 정보. 형식이 다르면 null.
 */
export function readPublicUser(value: unknown): PublicUser | null {
  if (!value || typeof value !== 'object') return null;
  if (!('id' in value) || typeof value.id !== 'string' || !value.id) return null;
  if (!('email' in value) || typeof value.email !== 'string' || !value.email) return null;
  return { id: value.id, email: value.email };
}

/** 백엔드 토큰과 만료 시각, 공개 계정을 함께 검증한다.
 * @param value FastAPI 내부 인증 응답.
 * @returns 유효한 내부 토큰 쌍 또는 null.
 */
export function readTokenPair(value: unknown): InternalTokenPair | null {
  if (!value || typeof value !== 'object') return null;
  const data = value as Partial<InternalTokenPair>;
  const user = readPublicUser(data.user);
  const access = data.access_token;
  const refresh = data.refresh_token;
  const accessExpiry = data.access_expires_at;
  const refreshExpiry = data.refresh_expires_at;
  if (!user || !accessExpiry || !refreshExpiry) return null;
  if (typeof accessExpiry !== 'string' || typeof refreshExpiry !== 'string') return null;
  if (typeof access !== 'string' || !/^[\w.-]+$/.test(access)) return null;
  if (typeof refresh !== 'string' || !/^[\w-]+$/.test(refresh)) return null;
  const accessTime = Date.parse(accessExpiry);
  const refreshTime = Date.parse(refreshExpiry);
  if (!(accessTime > Date.now() && refreshTime >= accessTime)) return null;
  return {
    user,
    access_token: access,
    refresh_token: refresh,
    access_expires_at: accessExpiry,
    refresh_expires_at: refreshExpiry,
  };
}
