import { useEffect } from 'react';
import type { GameState } from './types';
import { requestGame } from './game-client';

/** 처음 열 때 쿠키에 연결된 수사 기록을 불러온다.
 * @param setState 서버 수사 상태를 화면에 반영하는 함수.
 * @param setNotes 메모 입력값을 바꾸는 함수.
 * @param setError 화면의 오류 안내를 바꾸는 함수.
 * @param setReady 초기 자료 준비 여부를 바꾸는 함수.
 * @returns 없음. 초기 복원 효과를 등록한다.
 */
export function useRestoreGame(
  setState: (state: GameState | null) => void,
  setNotes: (notes: string) => void,
  setError: (message: string) => void,
  setReady: (ready: boolean) => void,
) {
  // 처음 열 때 쿠키에 연결된 수사 기록을 복원한다.
  useEffect(() => {
    let alive = true;
    requestGame('state')
      .then((savedState) => {
        if (alive) {
          setState(savedState);
          setNotes(savedState?.notes ?? '');
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
  }, []);
}
