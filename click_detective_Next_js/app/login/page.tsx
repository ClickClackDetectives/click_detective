import { AuthForm } from '@/components/auth/auth-form';
import { GuestAccount } from '@/components/auth/guest-account';

/** 로그인 화면과 가입 완료 안내를 표시한다.
 * @param props 로그인 화면의 검색 파라미터.
 * @returns 로그인 화면.
 */
export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ created?: string }>;
}) {
  const { created } = await searchParams;
  return (
    <GuestAccount>
      <AuthForm signup={false} created={created === '1'} />
    </GuestAccount>
  );
}
