import { ArrowRight, Fingerprint } from 'lucide-react';
import { evidence, suspects } from '@/app/game/catalog/catalog';
import type { GameState, SourceRef } from '@/app/game/investigation/types';
import type { CaseGameController } from '@/app/game/investigation/use-case-game';
type Props = Omit<Pick<CaseGameController, 'state' | 'openEvidence'>, 'state'> & {
  state: GameState;
};
/** 자료 종류와 ID를 합쳐 목록 식별자를 만든다.
 * @param ref 자료 종류와 ID가 담긴 출처.
 * @returns 자료 종류와 ID를 합친 문자열.
 */
function key(ref: SourceRef) {
  return ref.kind + ':' + ref.id;
}
/** 심문에서 확인한 사실만 표시한다. 자료 연결과 추론 생성은 별도 화면에서 처리한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.openEvidence 자료를 열람하고 문서 팝업을 여는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function FindingsScreen({ state, openEvidence }: Props) {
  /** 출처의 화면용 제목을 만든다.
   * @param ref 자료 종류와 ID가 담긴 출처.
   * @returns 확보 자료의 제목. 찾지 못하면 undefined.
   */
  function title(ref: SourceRef) {
    if (ref.kind === 'derived') return state.derivedEvidence[ref.id]?.title;
    if (ref.kind === 'testimony') return state.statements[ref.id]?.title;
    return evidence.find((item) => item.id === ref.id)?.title;
  }
  /** 선택한 출처의 자료를 연다.
   * @param ref 자료 종류와 ID가 담긴 출처.
   * @returns 없음. 선택한 자료를 여는 비동기 작업을 시작한다.
   */
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
        <p>심문에서 확인한 쟁점만 기록합니다. 제시한 자료와 용의자의 답변을 다시 확인하세요.</p>
      </div>{' '}
      <section className="findings-section">
        <h2>심문에서 확인한 쟁점</h2>
        {state.contradictions.length === 0 ? (
          <p className="empty">자료를 제시하며 심문하면 확인된 쟁점이 여기에 기록됩니다.</p>
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
                      {suspects.find((person) => person.id === detail.suspectId)?.name}의 심문에서
                      확인한 내용
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
