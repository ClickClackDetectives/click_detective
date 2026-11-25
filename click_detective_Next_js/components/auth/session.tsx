'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { hasSessionEnded, restoreSession } from '@/shared/auth/client';
import { bindAccount } from '@/shared/auth/scope';
import type { PublicUser } from '@/shared/auth/contract';
import { ApiError } from '@/shared/api/error';

type Session = {
  status: 'loading' | 'ready' | 'expired' | 'error' | 'disabled';
  user: PublicUser | null;
  error?: string;
};

const SessionContext = createContext<Session>({ status: 'loading', user: null });

/** 현재 수사 화면과 메뉴가 같은 계정 확인 결과를 사용하게 한다.
 * @param props 계정 확인 상태를 공유할 화면.
 * @returns 계정 정보를 전달하는 화면.
 */
export function AccountSession({ children }: { children: ReactNode }) {
  return <SessionContext.Provider value={useRestoreSession()}>{children}</SessionContext.Provider>;
}

/** 진입 시 계정을 확인하고 다른 탭의 세션 변경을 반영한다.
 * @returns 계정과 계정 확인 상태.
 */
function useRestoreSession() {
  const [session, setSession] = useState<Session>({ status: 'loading', user: null });
  useEffect(() => {
    let active = true;
    let expired = false;
    const channel =
      typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel('cd-session') : null;
    /** 현재 세션을 닫고 계정 수사 화면을 내린다.
     * @returns 없음. 계정 확인 상태를 만료로 바꾼다.
     */
    function expire() {
      expired = true;
      bindAccount(null);
      setSession({ status: 'expired', user: null });
    }
    /** 브라우저가 보관한 계정 화면을 복원하면 현재 세션부터 다시 확인한다.
     * @param event 브라우저의 페이지 표시 이벤트.
     * @returns 없음. 이전 계정 화면이 캐시에서 열리면 다시 로드한다.
     */
    function recheckCachedPage(event: PageTransitionEvent) {
      if (event.persisted && window.location.pathname !== '/') {
        expire();
        window.location.reload();
      }
    }
    window.addEventListener('pageshow', recheckCachedPage);
    window.addEventListener('cd-session-ended', expire);
    channel?.addEventListener('message', expire);
    restoreSession()
      .then((user) => {
        if (!active || expired) return;
        bindAccount(user?.id ?? null);
        setSession({ status: 'ready', user });
      })
      .catch((error) => {
        if (!active || expired) return;
        if (error instanceof ApiError && error.code === 'AUTH_DISABLED') {
          setSession({ status: 'disabled', user: null });
        } else if (hasSessionEnded(error)) {
          expire();
        } else {
          setSession({
            status: 'error',
            user: null,
            error: error instanceof Error ? error.message : '계정을 확인할 수 없습니다.',
          });
        }
      });
    return () => {
      active = false;
      channel?.close();
      window.removeEventListener('cd-session-ended', expire);
      window.removeEventListener('pageshow', recheckCachedPage);
    };
  }, []);
  return session;
}

/** 같은 화면의 계정 확인 결과를 읽는다.
 * @returns 공유된 계정과 상태.
 */
export function useSession() {
  return useContext(SessionContext);
}

/** 계정을 바꾸는 요청의 완료를 다른 탭에 알린다.
 * @returns 없음. 다른 탭에서 열린 이전 계정 화면을 내린다.
 */
export function announceAccountChange() {
  if (typeof BroadcastChannel === 'undefined') return;
  const channel = new BroadcastChannel('cd-session');
  channel.postMessage('changed');
  channel.close();
}
