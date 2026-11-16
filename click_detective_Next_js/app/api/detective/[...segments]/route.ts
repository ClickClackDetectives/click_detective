import { handle } from '@/server/proxy/handle';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export { handle as GET, handle as POST, handle as PUT };
