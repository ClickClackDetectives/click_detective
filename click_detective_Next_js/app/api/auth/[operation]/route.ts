import { handleAuth } from '@/server/auth/handle';

export const runtime = 'nodejs';
export const GET = handleAuth;
export const POST = handleAuth;
