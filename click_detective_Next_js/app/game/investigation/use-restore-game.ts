import { useEffect } from 'react';
import type { GameState } from './types';
import { requestGame } from './game-client';
import type { View } from '@/components/application/navigation';

/** 로그인 계정의 최근 수사 또는 직접 선택한 수사를 불러온다.
 * @param userId 확인한 현재 사용자 ID. 로그인 전에는 undefined.
 * @param setState 서버 수사 상태를 화면에 반영하는 함수.
 * @param setNotes 메모 입력값을 바꾸는 함수.
 * @param setError 화면의 오류 안내를 바꾸는 함수.
 * @param setReady 초기 자료 준비 여부를 바꾸는 함수.
 * @param setView 계정에서 연 수사의 화면을 표시하는 함수.
 * @returns 없음. 초기 복원 효과를 등록한다.
 */
export function useRestoreGame(
  userId: string | undefined,
  setState: (state: GameState | null) => void,
  setNotes: (notes: string) => void,
  setError: (message: string) => void,
  setReady: (ready: boolean) => void,
  setView: (view: View) => void,
) {
  // 계정이 바뀌면 이전 수사의 상태와 메모를 지운다.
  useEffect(() => {
    if (!userId) {
      setState(null);
      setNotes('');
      setView('home');
      setReady(true);
      return;
    }
    let alive = true;
    setState(null);
    setNotes('');
    setReady(false);
    requestGame('state')
      .then((savedState) => {
        if (alive) {
          setState(savedState);
          setNotes(savedState?.notes ?? '');
          if (savedState && window.location.pathname === '/game') {
            setView(savedState.verdict ? 'results' : 'briefing');
          }
        }
      })
      .catch(() => {
        if (alive) setError('기존 수사 기록을 불러오지 못했습니다. 새로고침 후 다시 시도하세요.');
      })
      .finally(() => {
        if (alive) setReady(true);
      });
    return () => {
      alive = false;
    };
  }, [userId, setState, setNotes, setError, setReady, setView]);
}
