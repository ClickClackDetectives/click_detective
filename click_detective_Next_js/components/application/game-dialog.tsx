import { Check, Gavel, X, RotateCcw } from 'lucide-react';

import type { CaseGameController } from '@/app/game/investigation/use-case-game';

type Props = Pick<
  CaseGameController,
  'modal' | 'busy' | 'setModal' | 'updateGame' | 'form' | 'navigateTo' | 'startInvestigation'
>;

const dialogContent: Record<string, { title: string; description: string }> = {
  login: { title: '로그인을 하세요', description: '사건을 진행하려면 로그인이 필요합니다.' },
  confirm: {
    title: '고발을 확정하시겠습니까?',
    description:
      '제출 후에는 현재 수사의 질문과 기록을 변경할 수 없습니다. 결과 화면에서 새로운 수사를 시작할 수 있습니다.',
  },
  restart: {
    title: '새로 수사하시겠습니까?',
    description: '현재 수사 기록과 노트가 초기화됩니다. 사건을 처음부터 다시 시작합니다.',
  },
  pack: {
    title: '다음 사건을 준비 중입니다.',
    description:
      '현재는 열세 번째 종 한 사건만 플레이할 수 있습니다. 후속 사건이나 결제는 제공하지 않습니다.',
  },
  record: {
    title: '첫 수사를 시작해 보세요.',
    description: '사건을 시작하면 진행 상황과 메모가 이 브라우저의 수사 세션에 저장됩니다.',
  },
  about: {
    title: '진실을 찾는 작은 실험.',
    description:
      '사용자가 제공한 열세 번째 종 시나리오를 기반으로 구성한 Next.js 추리게임입니다. 현재 심문은 FastAPI에 연결되어 있으며, 백엔드의 실행 모드에 따라 Qwen·멀티 에이전트 또는 테스트 응답을 사용합니다. 추론 증거 2개 이상·심문 쟁점 2개 이상 확보 후 증거실에서 2차 조사를 열 수 있습니다. 질문은 수사 전체 25회이며 증거를 첨부한 심문도 포함됩니다. 수사 기록은 서버에 저장됩니다.',
  },
};

/** 고발 확인·수사 초기화·도움말 팝업을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.modal 열린 안내 팝업 이름.
 * @param props.busy 요청 처리 중인지 여부.
 * @param props.setModal 안내 팝업을 열거나 닫는 함수.
 * @param props.updateGame 행동 이름과 입력을 서버에 보내고 최신 상태를 적용하는 함수.
 * @param props.form 고발 대상·동기·방법·근거 입력.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @param props.startInvestigation 기존 수사를 이어가거나 새 수사를 만드는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function GameDialog({
  modal,
  busy,
  setModal,
  updateGame,
  form,
  navigateTo,
  startInvestigation,
}: Props) {
  if (!modal) return null;
  const content = dialogContent[modal] ?? dialogContent.about;
  return (
    <div className="modal-backdrop" onClick={() => !busy && setModal(null)}>
      <section
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          autoFocus
          className="close-modal"
          disabled={busy}
          aria-label="안내 닫기"
          onClick={() => setModal(null)}
        >
          <X size={20} />
        </button>
        <div className="eyebrow">THE THIRTEENTH BELL · FIELD NOTES</div>
        <h2 id="modal-title">{content.title}</h2>
        <p>{content.description}</p>
        <div className="modal-actions">
          {modal === 'login' ? (
            <a className="primary" href="/login">
              로그인
            </a>
          ) : modal === 'confirm' ? (
            <>
              <button className="outline" onClick={() => setModal(null)} disabled={busy}>
                다시 검토
              </button>
              <button
                className="primary"
                disabled={busy}
                onClick={async () => {
                  const updatedState = await updateGame('accuse', form);
                  setModal(null);
                  if (updatedState) navigateTo('results');
                }}
              >
                {busy ? '제출 중…' : '고발 확정'}
                <Gavel size={15} />
              </button>
            </>
          ) : modal === 'restart' ? (
            <button className="primary" disabled={busy} onClick={() => startInvestigation(true)}>
              기록 초기화 후 시작 <RotateCcw size={15} />
            </button>
          ) : (
            <button
              className="primary"
              onClick={() => {
                setModal(null);
                if (modal === 'record') navigateTo('cases');
              }}
            >
              확인 <Check size={15} />
            </button>
          )}
        </div>
      </section>
    </div>
  );
}
