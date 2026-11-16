import { useEffect, useRef } from 'react';
import type { GameState } from '../investigation/types';
import { requestGame } from '../investigation/game-client';

type Options = {
  state: GameState | null;
  notes: string;
  busy: boolean;
  setState: (state: GameState | null) => void;
  setNoteStatus: (status: string) => void;
};

/** 입력이 멈추면 저장하고, 저장하지 않은 메모가 있으면 탭 종료를 알린다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.notes 현재 입력 중인 수사 메모.
 * @param props.busy 요청 처리 중인지 여부.
 * @param props.setState 서버 수사 상태를 화면에 반영하는 함수.
 * @param props.setNoteStatus 메모 저장 상태 안내를 바꾸는 함수.
 * @returns 없음. 메모 자동 저장과 종료 안내 효과를 등록한다.
 */
export function useNotesAutosave({ state, notes, busy, setState, setNoteStatus }: Options) {
  const stateRef = useRef(state);
  stateRef.current = state;
  const latestNotes = useRef(notes);
  latestNotes.current = notes;
  // 입력이 700ms 동안 멈추면 저장한다. 오래된 응답이 최신 입력을 덮어쓰지 않게 한다.
  useEffect(() => {
    if (!state || state.verdict || notes === state.notes || busy) return;
    setNoteStatus('저장 대기 중');
    const timer = setTimeout(() => {
      const snapshot = notes;
      setNoteStatus('저장 중…');
      requestGame('notes', { text: snapshot })
        .then((savedState) => {
          if (!savedState) throw new Error('수사 기록이 없습니다.');
          if (latestNotes.current === snapshot) {
            setState(savedState);
            setNoteStatus('저장됨');
          }
        })
        .catch(() => setNoteStatus('저장 실패 · 다시 저장을 눌러주세요'));
    }, 700);
    return () => clearTimeout(timer);
  }, [notes, state?.notes, state?.id, state?.verdict, busy]);
  useEffect(() => {
    /** 현재 화면의 키보드 또는 탭 종료 이벤트를 처리한다.
     * @param e 사용자 입력 또는 키보드 이벤트.
     * @returns 없음. 브라우저 이벤트와 화면 상태를 처리한다.
     */
    const handler = (e: BeforeUnloadEvent) => {
      if (stateRef.current && latestNotes.current !== stateRef.current.notes) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, []);
}
