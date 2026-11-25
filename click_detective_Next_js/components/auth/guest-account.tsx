'use client';

import { useEffect } from 'react';
import type { ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { AccountSession, useSession } from './session';

/** 계정 세션을 확인한 뒤 비로그인 사용자에게 인증 화면을 표시한다.
 * @param props 로그인 또는 회원가입 화면에 표시할 내용.
 * @returns 세션 확인과 폼 표시를 연결한 화면.
 */
export function GuestAccount({ children }: { children: ReactNode }) {
  return (
    <AccountSession>
      <GuestContent>{children}</GuestContent>
    </AccountSession>
  );
}

/** 활성 세션이 있으면 메인 화면으로 이동하고 세션 확인 전에는 폼을 숨긴다.
 * @param props 로그인 또는 회원가입 화면에 표시할 내용.
 * @returns 비로그인 사용자용 폼 또는 세션 확인과 이동 중에는 null.
 */
function GuestContent({ children }: { children: ReactNode }) {
  const { user, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (user) router.replace('/');
  }, [router, user]);

  if (user || status === 'loading') return null;
  return children;
}
