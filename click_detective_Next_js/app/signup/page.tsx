import { AuthForm } from '@/components/auth/auth-form';
import { GuestAccount } from '@/components/auth/guest-account';

/** 회원가입 화면을 표시한다.
 * @returns 이메일과 비밀번호를 받는 화면.
 */
export default function SignupPage() {
  return (
    <GuestAccount>
      <AuthForm signup />
    </GuestAccount>
  );
}
