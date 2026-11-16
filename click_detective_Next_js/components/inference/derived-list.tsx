import { ArrowRight } from 'lucide-react';
import type { GameState, SourceRef } from '../../app/game/investigation/types';
import type { CaseGameController } from '../../app/game/investigation/use-case-game';
import { getInferenceBasisLabel, sourceKey as key } from '../../app/game/inference/sources';

type Props = {
  state: GameState;
  openEvidence: CaseGameController['openEvidence'];
  title: (source: SourceRef) => string;
  open: (source: SourceRef) => void;
};

/** 이미 확보한 추론 문서와 직접·원본 근거를 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.openEvidence 자료를 열람하고 문서 팝업을 여는 함수.
 * @param props.title 출처의 표시 제목을 만드는 함수.
 * @param props.open 선택한 출처를 여는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function DerivedList({ state, openEvidence, title, open }: Props) {
  const derived = Object.values(state.derivedEvidence);
  return (
    <section className="findings-section">
      <h2>
        추론 증거 <small aria-live="polite">{derived.length}개</small>
      </h2>
      {derived.length === 0 ? (
        <p className="empty">아직 생성한 추론 증거가 없습니다.</p>
      ) : (
        <div className="derived-grid">
          {derived.map((item) => (
            <article className="panel" key={item.id}>
              <span className="eyebrow">{item.code} · 추론 증거</span>
              <span className="inference-kind">
                {item.investigationPhase === 1 ? '1차 전용' : '2차 조사'} ·{' '}
                {item.construction === 'chain' ? '연쇄 추론' : '기본 추론'}
              </span>
              <h3>{item.title}</h3>
              <span className="inference-kind">
                {getInferenceBasisLabel(state, item.leafSources)}
              </span>
              <h4>도출한 결론</h4>
              <p>{item.body}</p>
              <h4>직접 연결한 자료</h4>
              <div className="source-links">
                {item.sourceRefs.map((ref) => (
                  <button key={key(ref)} onClick={() => open(ref)}>
                    {title(ref)} <ArrowRight size={12} />
                  </button>
                ))}
              </div>
              <details className="inference-origins">
                <summary>원본 근거 {item.leafSources.length}개 확인</summary>
                <div className="source-links">
                  {item.leafSources.map((ref) => (
                    <button key={key(ref)} onClick={() => open(ref)}>
                      {title(ref)} <ArrowRight size={12} />
                    </button>
                  ))}
                </div>
              </details>
              <button className="text-button" onClick={() => openEvidence(item.id)}>
                증거 열람·심문에 제시 <ArrowRight size={14} />
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
