/** 화면이 사용하는 오류입니다. API 키나 서버 내부 스택은 포함하지 않습니다. */
export class ApiError extends Error {
  status: number;
  code: string;
  constructor(message: string, status: number, code: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}
/** 모든 브라우저 호출은 같은 출처의 Next.js BFF를 통합니다. */
export async function api<T>(
  path: string,
  method = 'GET',
  body?: unknown,
): Promise<T> {
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
/** 백엔드가 준 자산 경로를 같은 출처 프록시 경로로 바꿉니다. 임의 외부 URL은 받지 않습니다. */
export function assetUrl(path: string): string {
  if (path.startsWith('/v1/assets/'))
    return '/api/detective/assets/' + path.slice('/v1/assets/'.length);
  const match = path.match(/^\/v1\/games\/[^/]+\/evidence-assets\/([^/]+)$/);
  return match
    ? '/api/detective/evidence-assets/' + encodeURIComponent(match[1])
    : '';
}
