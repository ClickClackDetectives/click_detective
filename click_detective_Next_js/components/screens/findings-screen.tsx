import { ArrowRight, Fingerprint } from 'lucide-react';
import { evidence, suspects, type GameState, type SourceRef } from '@/lib/case';
import type { CaseGameController } from '@/hooks/use-case-game';
type Props = Omit<Pick<CaseGameController, 'state' | 'openEvidence'>, 'state'> & {
  state: GameState;
};
function key(ref: SourceRef) {
  return ref.kind + ':' + ref.id;
}
/** 심문에서 확인한 사실만 표시한다. 자료 연결과 추론 생성은 별도 화면에서 처리한다. */
export function FindingsScreen({ state, openEvidence }: Props) {
  function title(ref: SourceRef) {
    return ref.kind === 'derived'
      ? state.derivedEvidence[ref.id]?.title
      : ref.kind === 'testimony'
        ? state.statements[ref.id]?.title
        : evidence.find((item) => item.id === ref.id)?.title;
  }
  function open(ref: SourceRef) {
    void openEvidence(ref.id);
  }
  return (
    <>
      <div className="desk-heading">
        <div className="eyebrow">INTERROGATION FINDINGS</div>
        <h1>
          발견한 쟁점<span>.</span>
        </h1>
        <p>
          심문에서 확인한 쟁점만 기록합니다. 제시한 자료와 용의자의 답변을 다시
          확인하세요.
        </p>
      </div>{' '}
      <section className="findings-section">
        <h2>심문에서 확인한 쟁점</h2>
        {state.contradictions.length === 0 ? (
          <p className="empty">
            자료를 제시하며 심문하면 확인된 쟁점이 여기에 기록됩니다.
          </p>
        ) : (
          state.contradictions.map((finding) => {
            const detail = state.findingDetails.find((item) => item.title === finding);
            return (
              <article className="panel finding-card" key={finding}>
                <h3>
                  <Fingerprint size={17} />
                  {finding}
                </h3>
                {detail && (
                  <>
                    <p>
                      {suspects.find((person) => person.id === detail.suspectId)?.name}의
                      심문에서 확인한 내용
                    </p>
                    <div className="source-links">
                      {detail.sourceRefs.map((ref) => (
                        <button key={key(ref)} onClick={() => open(ref)}>
                          {title(ref)} <ArrowRight size={12} />
                        </button>
                      ))}
                    </div>
                    <blockquote>{state.messages[detail.messageIndex]?.text}</blockquote>
                  </>
                )}
              </article>
            );
          })
        )}
      </section>
    </>
  );
}
