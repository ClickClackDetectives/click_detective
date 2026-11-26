import { AccountSession } from '@/components/auth/session';
import { OriginalAppLoader } from '@/components/application/original-app-loader';
/** 사건 자료를 준비하는 첫 화면을 표시한다.
 * 파라미터 없음.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export default function Page() {
  return (
    <AccountSession>
      <OriginalAppLoader />
    </AccountSession>
  );
}
