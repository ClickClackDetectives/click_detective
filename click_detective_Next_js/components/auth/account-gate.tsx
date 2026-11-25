'use client';

import type { ReactNode } from 'react';
import { AccountFrame } from './account-frame';
import { AccountSession, useSession } from './session';

/** 계정이 확인된 경우에만 보호 화면을 표시한다.
 * @param props 요청한 목적지와 보호 화면.
 * @returns 계정 화면 또는 로그인·오류 안내.
 */
export function AccountGate({
  destination,
  children,
}: {
  destination: string;
  children: ReactNode;
}) {
  return (
    <AccountSession>
      <ProtectedAccount destination={destination}>{children}</ProtectedAccount>
    </AccountSession>
  );
}

/** 공유된 계정이 활성 상태인지 확인해 보호 화면을 표시한다.
 * @param props 다시 확인할 경로와 보호 화면.
 * @returns 승인된 수사 화면 또는 계정 확인 안내.
 */
function ProtectedAccount({ destination, children }: { destination: string; children: ReactNode }) {
  const session = useSession();
  if (session.user) return children;
  return (
    <AccountFrame title="내 수사">
      {session.status === 'loading' ? (
        <p role="status">계정을 확인하고 있습니다.</p>
      ) : session.status === 'error' || session.status === 'disabled' ? (
        <>
          <p role="alert">{session.error ?? '현재 계정 기능을 사용할 수 없습니다.'}</p>
          <a href={destination}>다시 확인</a>
        </>
      ) : (
        <>
          <p>수사를 열려면 로그인하세요.</p>
          <a href="/login">로그인</a>
        </>
      )}
    </AccountFrame>
  );
}
