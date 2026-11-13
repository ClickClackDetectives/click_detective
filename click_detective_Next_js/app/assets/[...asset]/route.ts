import type { NextRequest } from 'next/server';
import { GET as proxy } from '@/app/api/detective/[...segments]/route';
/** 원본 자산 URL은 유지하고 실제 파일은 인증된 FastAPI에서 받습니다. */
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ asset: string[] }> },
) {
  const { asset } = await context.params;
  return proxy(request, {
    params: Promise.resolve({ segments: ['assets', 'assets', ...asset] }),
  });
}
