'use client';

import { useRef, useState } from 'react';
import { authRequest, withAuthLock } from '@/shared/auth/client';
import { notifySessionEnd } from '@/shared/auth/scope';
import { announceAccountChange, useSession } from './session';
import './account.css';

/** 헤더의 같은 위치에서 로그인 링크 또는 현재 계정과 로그아웃을 표시한다.
 * @returns 상단 계정 메뉴.
 */
export function AccountControls() {
  const { user } = useSession();
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const working = useRef(false);

  /** 현재 계정의 세션을 폐기한 후 메인 화면으로 이동한다.
   * @returns 로그아웃 처리의 완료를 기다리는 Promise.
   */
  async function logout() {
    if (!user || working.current) return;
    working.current = true;
    setBusy(true);
    setError('');
    try {
      await withAuthLock(() => authRequest('logout', undefined, user.id));
      notifySessionEnd();
      announceAccountChange();
      window.location.replace('/');
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : '로그아웃에 실패했습니다.');
    } finally {
      setBusy(false);
      working.current = false;
    }
  }

  if (!user) {
    return (
      <a className="outline small" data-account-entry href="/login">
        로그인
      </a>
    );
  }
  return (
    <div className="header-account" data-account-entry>
      <span className="header-account-email" title={user.email}>
        {user.email}
      </span>
      <button className="outline small" disabled={busy} onClick={() => void logout()}>
        로그아웃
      </button>
      {error && <span role="alert">{error}</span>}
    </div>
  );
}
