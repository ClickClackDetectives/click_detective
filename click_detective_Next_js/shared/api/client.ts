/** 화면이 사용하는 오류입니다. API 키나 서버 내부 스택은 포함하지 않습니다.
 * @param message 사용자에게 보여줄 안내.
 * @param status HTTP 상태 코드.
 * @param code 오류를 구분할 코드.
 * @returns ApiError 객체.
 */
export class ApiError extends Error {
  status: number;
  code: string;
  /** 객체에서 함께 사용할 값과 초기 상태를 준비한다.
   * @param message 사용자에게 보여줄 안내.
   * @param status HTTP 상태 코드.
   * @param code 오류를 구분할 코드.
   * @returns 없음. 객체의 초기값을 저장한다.
   */
  constructor(message: string, status: number, code: string) {
    super(message);
    this.status = status;
    this.code = code;
  }
}
/** 모든 브라우저 호출은 같은 출처의 Next.js BFF를 통합니다.
 * @param path 호출 경로나 파일 경로.
 * @param method HTTP 요청 메서드.
 * @param body 전송할 요청 본문.
 * @returns 서버가 반환한 JSON 응답.
 */
export async function api<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
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
/** 백엔드가 준 자산 경로를 같은 출처 프록시 경로로 바꿉니다. 임의 외부 URL은 받지 않습니다.
 * @param path 호출 경로나 파일 경로.
 * @returns 같은 출처의 자산 프록시 경로. 허용되지 않으면 빈 문자열.
 */
export function assetUrl(path: string): string {
  if (path.startsWith('/v1/assets/'))
    return '/api/detective/assets/' + path.slice('/v1/assets/'.length);
  const match = path.match(/^\/v1\/games\/[^/]+\/evidence-assets\/([^/]+)$/);
  return match ? '/api/detective/evidence-assets/' + encodeURIComponent(match[1]) : '';
}
