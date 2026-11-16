import { ArrowUpRight, Check, MessageSquare } from 'lucide-react';
import { evidence } from '../../app/game/catalog/catalog';
import type { GameState } from '../../app/game/investigation/types';
import type { CaseGameController } from '../../app/game/investigation/use-case-game';
import type { TestimonyView } from '../../app/game/materials/use-screen-view';
import { StatementEntry } from './statement-entry';
import { matchesSection } from '../../app/game/testimony/sections';

type Props = Pick<CaseGameController, 'busy' | 'openEvidence' | 'navigateTo'> & {
  state: GameState;
  w: TestimonyView['visible'][number];
  section: string;
};

/** 한 인물의 최초 진술, 확보 증언과 심문 대화를 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.w 한 인물의 서버 조회 결과.
 * @param props.section 선택한 증언 분류.
 * @param props.busy 요청 처리 중인지 여부.
 * @param props.openEvidence 자료를 열람하고 문서 팝업을 여는 함수.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function WitnessSection({ state, w, section, busy, openEvidence, navigateTo }: Props) {
  return (
    <section className="archive-section" aria-label={w.name}>
      <h2>
        <MessageSquare size={18} /> {w.name}
      </h2>
      {(section === 'all' ? w.records : []).map((item) => (
        <button
          key={item.id}
          className="evidence-card testimony-record"
          disabled={busy || (!!state.verdict && !state.examined.includes(item.id))}
          onClick={() => openEvidence(item.id)}
        >
          <div className="evidence-card-top">
            <span>{item.code} · 증언</span>
            {state.examined.includes(item.id) && (
              <span className="read-label">
                <Check size={12} />
                열람 완료
              </span>
            )}
          </div>
          <h3>{item.title}</h3>
          <p>{item.summary}</p>
          <span className="text-button">
            증언 열람 <ArrowUpRight size={14} />
          </span>
        </button>
      ))}
      {section === 'all' && w.initial && (
        <article className="panel testimony-entry">
          <span className="eyebrow">최초 진술</span>
          <p>{w.initial}</p>
        </article>
      )}
      {w.acquired
        .filter((item) => matchesSection(item, section))
        .map((item) => (
          <StatementEntry
            key={item.id}
            state={state}
            item={item}
            openEvidence={openEvidence}
            navigateTo={navigateTo}
          />
        ))}
      {(section === 'all' || section === 'transcript' ? w.pairs : []).map(
        ({ question, answer }) => (
          <article className="panel testimony-entry" key={question.index}>
            <span className="eyebrow">심문 기록</span>
            <p>
              <strong>수사관</strong> · {question.text}
            </p>
            {question.evidenceId && (
              <button className="text-button" onClick={() => openEvidence(question.evidenceId!)}>
                {'제시 자료:'}{' '}
                {state.derivedEvidence[question.evidenceId]?.code ?? question.evidenceId} {'·'}{' '}
                {state.derivedEvidence[question.evidenceId]?.title ??
                  evidence.find((item) => item.id === question.evidenceId)?.title}{' '}
                <ArrowUpRight size={13} />
              </button>
            )}
            {answer && (
              <blockquote>
                <strong>{w.name}</strong> · {answer.text}
              </blockquote>
            )}
          </article>
        ),
      )}
    </section>
  );
}
