import type { NextRequest } from 'next/server';
import { GET as proxy } from '@/app/api/detective/[...segments]/route';
/** 원본 자산 URL은 유지하고 실제 파일은 인증된 FastAPI에서 받습니다.
 * @param request 확인하거나 전달할 요청.
 * @returns 자산을 전달하는 HTTP 응답.
 */
export async function GET(request: NextRequest) {
  return proxy(request, {
    params: Promise.resolve({ segments: ['assets', 'manor.jpg'] }),
  });
}
