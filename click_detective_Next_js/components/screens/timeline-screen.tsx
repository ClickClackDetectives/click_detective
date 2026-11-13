import { ArrowUpRight } from 'lucide-react';
import { suspects, type GameState } from '@/lib/case';
import type { CaseGameController } from '@/hooks/use-case-game';
type Props = Pick<CaseGameController, 'busy' | 'openEvidence'> & { state: GameState };
export function TimelineScreen({ busy, openEvidence, state }: Props) {
  const times = [...new Set(state.timeline.map((item) => item.start))];
  return (
    <>
      <div className="desk-heading">
        <div className="eyebrow">RECONSTRUCT THE NIGHT</div>
        <h1>
          사건 타임라인<span>.</span>
        </h1>
        <p>
          공개 일정에서 시작해 확보한 자료와 진술로 시간축을 채우세요.
          진술·인정·검시·추론은 구분해서 기록합니다.
        </p>
      </div>
      <div className="timeline">
        {times.map((start) => (
          <section
            className="timeline-time-group"
            key={start}
            aria-label={`${Math.floor(start / 60)}:${String(start % 60).padStart(2, '0')} 시간대`}
          >
            {state.timeline
              .filter((item) => item.start === start)
              .map((item) => (
                <article key={item.id} id={'timeline-' + item.id}>
                  <time>{item.time}</time>
                  <div
                    className={'timeline-dot ' + (item.id === 'body-found' ? 'red' : '')}
                  />
                  <div>
                    <span className="eyebrow">
                      {item.category}
                      {item.speaker &&
                        ' · ' +
                          suspects.find((person) => person.id === item.speaker)?.name}
                      {item.end !== undefined && ' · 시간 범위'}
                    </span>
                    <h3>{item.title}</h3>
                    <p>{item.text}</p>
                    {item.statementId && (
                      <button
                        className="text-button"
                        disabled={busy}
                        onClick={() => openEvidence(item.statementId!)}
                      >
                        증언 원문·출처 확인 <ArrowUpRight size={13} />
                      </button>
                    )}
                    {item.evidenceId && (
                      <button
                        className="text-button"
                        disabled={busy}
                        onClick={() => openEvidence(item.evidenceId!)}
                      >
                        관련 자료 열람 <ArrowUpRight size={13} />
                      </button>
                    )}
                    {item.derivedId && (
                      <button
                        className="text-button"
                        disabled={busy}
                        onClick={() => openEvidence(item.derivedId!)}
                      >
                        추론 증거 열람 <ArrowUpRight size={13} />
                      </button>
                    )}
                  </div>
                </article>
              ))}
          </section>
        ))}
      </div>
    </>
  );
}
