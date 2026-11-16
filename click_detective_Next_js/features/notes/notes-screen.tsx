import { Check, StickyNote, Search } from 'lucide-react';
import type { GameState } from '@/features/investigation/types';
import type { CaseGameController } from '@/features/investigation/use-case-game';

type Props = Omit<
  Pick<
    CaseGameController,
    'state' | 'notes' | 'setNotes' | 'noteStatus' | 'busy' | 'updateGame' | 'setNoteStatus'
  >,
  'state'
> & { state: GameState };

/** 메모 입력창과 저장 상태를 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.notes 현재 입력 중인 수사 메모.
 * @param props.setNotes 메모 입력값을 바꾸는 함수.
 * @param props.noteStatus 메모 저장 상태를 보여주는 안내 문구.
 * @param props.busy 요청 처리 중인지 여부.
 * @param props.updateGame 행동 이름과 입력을 서버에 보내고 최신 상태를 적용하는 함수.
 * @param props.setNoteStatus 메모 저장 상태 안내를 바꾸는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function NotesScreen({
  state,
  notes,
  setNotes,
  noteStatus,
  busy,
  updateGame,
  setNoteStatus,
}: Props) {
  return (
    <>
      <div className="desk-heading">
        <div className="eyebrow">DETECTIVE’S NOTEBOOK</div>
        <h1>
          수사 노트<span>.</span>
        </h1>
        <p>사소한 의심도 기록하세요. 다음 단서가 될 수 있습니다.</p>
      </div>
      <div className="notebook">
        <div className="notebook-top">
          <span>
            <StickyNote size={16} /> CASE #0001 · 개인 기록
          </span>
          <div className="notebook-emblem" aria-hidden="true">
            <span>❧</span>
            <Search size={24} />
            <span>❧</span>
          </div>
          <span role="status">{state.verdict ? '종결 · 읽기 전용' : noteStatus}</span>
        </div>
        <textarea
          aria-label="수사 메모"
          placeholder={
            '누가 접근할 수 있었는가?\n누가 시간에 대해 거짓말했는가?\n\n당신의 가설을 이곳에 기록하세요.'
          }
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          maxLength={20000}
          readOnly={!!state.verdict}
        />
        <div className="notebook-bottom">
          <span>{notes.length.toLocaleString()} / 20,000자 · 자동 저장</span>
          <button
            className="text-button"
            disabled={busy || !!state.verdict || notes === state.notes}
            onClick={async () => {
              const updatedState = await updateGame('notes', { text: notes });
              setNoteStatus(updatedState ? '저장됨' : '저장 실패 · 다시 시도하세요');
            }}
          >
            지금 저장 <Check size={14} />
          </button>
        </div>
      </div>
    </>
  );
}
