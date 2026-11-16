import { ArrowUpRight } from 'lucide-react';
import type { GameState, AcquiredStatement } from '../investigation/types';
import type { CaseGameController } from '../investigation/use-case-game';

type Props = Pick<CaseGameController, 'openEvidence' | 'navigateTo'> & {
  state: GameState;
  item: AcquiredStatement;
};

/** 획득한 진술과 수정 이력, 출처, 타임라인 이동을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.item 확인할 자료 또는 진술.
 * @param props.openEvidence 자료를 열람하고 문서 팝업을 여는 함수.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function StatementEntry({ state, item, openEvidence, navigateTo }: Props) {
  return (
    <article className="panel testimony-entry" key={item.id} id={'statement-' + item.id}>
      <span className="eyebrow">
        {item.code} · {item.nature} {item.time && ' · ' + item.time}
      </span>
      <h3>{item.title}</h3>
      <p>{item.excerpt}</p>
      {Object.values(state.statements).some((next) => next.supersedes?.includes(item.id)) && (
        <p className="subtle">
          이 주장과 다른 이후 인정이 확보되었습니다. 이전 발언은 원문대로 보존합니다.
        </p>
      )}
      {item.supersedes?.some((id) => !!state.statements[id]) && (
        <p className="subtle">기존 체류 주장에 대한 수정 진술입니다.</p>
      )}
      <div className="source-links">
        <button onClick={() => openEvidence(item.id)}>
          심문 원문 <ArrowUpRight size={12} />
        </button>
        {item.time && (
          <button
            onClick={() => {
              navigateTo('timeline');
              setTimeout(
                () =>
                  document
                    .getElementById('timeline-statement-' + item.id)
                    ?.scrollIntoView({ behavior: 'smooth', block: 'center' }),
                0,
              );
            }}
          >
            타임라인 <ArrowUpRight size={12} />
          </button>
        )}
        {item.sourceRefs.map((ref) => (
          <button key={ref.kind + ref.id} onClick={() => openEvidence(ref.id)}>
            제시 자료 {ref.id} <ArrowUpRight size={12} />
          </button>
        ))}
      </div>
      <details>
        <summary>대본 출처</summary>
        <p>
          {item.source.file} · {item.source.pages.join(', ')}쪽 · {item.source.section}
        </p>
      </details>
    </article>
  );
}
