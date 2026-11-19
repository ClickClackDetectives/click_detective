import { getInvestigationProgress } from '@/app/game/investigation/progress';
import { ArrowRight, CheckCheck, Shield, X, RotateCcw } from 'lucide-react';
import type { GameState, ReviewItem } from '@/app/game/investigation/types';
import type { CaseGameController } from '@/app/game/investigation/use-case-game';

type Props = Omit<Pick<CaseGameController, 'state' | 'setModal' | 'navigateTo'>, 'state'> & {
  state: GameState;
};

/** 고발 결과와 발견·미발견 항목을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.setModal 안내 팝업을 열거나 닫는 함수.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function ResultsScreen({ state, setModal, navigateTo }: Props) {
  const verdict = state.verdict;
  if (!verdict) return null;
  const progress = getInvestigationProgress(state);
  const review = verdict.review;
  return (
    <div className="results">
      <div className="result-seal">
        <Shield size={45} />
      </div>
      <div className="eyebrow">INVESTIGATION COMPLETE</div>
      <h1>{verdict.correct ? '진실을 밝혀냈습니다.' : '아직, 풀리지 않은 진실.'}</h1>
      <p>
        {verdict.correct
          ? '범인 검거에 필요한 핵심 입증을 완료했습니다.'
          : '증거가 말하는 이야기와 당신의 결론을 비교해 보세요.'}
      </p>
      <section className="result-progress" aria-label="수사 진행도">
        <div className="eyebrow">수사 진행도</div>
        <div className="result-progress-value">
          {progress.percent}
          <span>%</span>
        </div>
        <div
          className="progress-track"
          role="progressbar"
          aria-label="수사 진행도"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={progress.percent}
        >
          <i style={{ width: `${progress.percent}%` }} />
        </div>
        <p>수집한 자료·쟁점·추론의 완성도이며, 100%는 범인 검거 조건이 아닙니다.</p>
      </section>
      <div className="result-checks">
        {verdict.checks.map((c) => (
          <details key={c.label}>
            <summary>
              {c.correct ? <CheckCheck size={18} /> : <X size={18} />}
              <span>{c.label}</span>
              <strong>{c.correct ? '입증 완료' : '입증 실패'}</strong>
            </summary>
            <div className="result-check-detail">
              {c.label === '범인 지목' && <p>{verdict.checkDetails?.['범인 지목']}</p>}
              {c.label === '범행 동기' && <p>{verdict.checkDetails?.['범행 동기']}</p>}
              {c.label === '범행 수단' && <p>{verdict.checkDetails?.['범행 수단']}</p>}
              {c.label === '핵심 증거 연결' && (
                <>
                  <p>{verdict.checkDetails?.['핵심 증거 연결']}</p>
                  {verdict.evidenceAssessment && (
                    <section className="result-evidence-assessment">
                      <h2>핵심 증거 연결 근거</h2>
                      <p>제출한 원본 물증과 추론 증거에 포함된 원본 물증을 함께 판정했습니다.</p>
                      {verdict.evidenceAssessment.submitted.map((item) => (
                        <article key={item.id}>
                          <strong>
                            {item.kind === 'derived' ? '[추론 증거] ' : '[원본 증거] '}
                            {item.title}
                          </strong>
                          <span>{item.contributes ? '핵심 근거에 포함' : '보조 근거'}</span>
                          {item.coveredTitles.length > 0 && (
                            <p>연결된 핵심 물증: {item.coveredTitles.join(' · ')}</p>
                          )}
                        </article>
                      ))}
                      {verdict.evidenceAssessment.missing.length > 0 && (
                        <div className="missing-core">
                          <h3>추가로 필요한 핵심 물증</h3>
                          <ul>
                            {verdict.evidenceAssessment.missing.map((item) => (
                              <li key={item.id}>{item.title}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </section>
                  )}
                </>
              )}
            </div>
          </details>
        ))}
      </div>
      <div className="solution">
        <span className="eyebrow">THE TRUTH BEHIND THE CASE</span>
        <p>{verdict.explanation}</p>
      </div>
      {review && (
        <section className="result-discoveries">
          <h2>발견 기록</h2>
          <DiscoveryGroup title="심문에서 확인한 쟁점" items={review.findings} />
          <DiscoveryGroup title="추론 증거" items={review.inference} />
        </section>
      )}
      <div className="result-actions">
        <button className="outline" onClick={() => setModal('restart')}>
          <RotateCcw size={15} /> 다시 수사하기
        </button>
        <button className="primary" onClick={() => navigateTo('cases')}>
          사건 기록실 <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
}

/** 결과 항목을 발견 여부에 따라 나누어 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.title 발견 목록 위에 표시할 제목.
 * @param props.items 발견 여부를 나누어 표시할 항목 목록.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
function DiscoveryGroup({ title, items }: { title: string; items: ReviewItem[] }) {
  const found = items.filter((item) => item.discovered);
  const missing = items.filter((item) => !item.discovered);
  return (
    <section className="discovery-group">
      <h3>{title}</h3>
      <div className="discovery-columns">
        <section>
          <h4>
            <CheckCheck size={15} />
            발견
          </h4>
          {found.length === 0 ? (
            <p className="discovery-empty">발견한 항목이 없습니다.</p>
          ) : (
            <ul>
              {found.map((item) => (
                <li key={item.id}>
                  {item.title}
                  {item.submitted && <span className="submitted-badge">고발에 제출</span>}
                </li>
              ))}
            </ul>
          )}
        </section>
        <section>
          <h4>
            <X size={15} />
            미발견
          </h4>
          {missing.length === 0 ? (
            <p className="discovery-empty">모든 항목을 발견했습니다.</p>
          ) : (
            <ul>
              {missing.map((item) => (
                <li key={item.id}>
                  {item.title}
                  {item.submitted && <span className="submitted-badge">고발에 제출</span>}
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </section>
  );
}
