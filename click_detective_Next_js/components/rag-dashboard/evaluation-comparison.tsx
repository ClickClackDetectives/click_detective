import { useState } from 'react';
import { metricDefinitions, percent, type Cohort } from '@/app/game/rag-dashboard/metrics';

/** 같은 평가 질문에서 기준선과 하이브리드의 지표를 비교한다.
 * @param props 비교할 질문 집합 목록.
 * @param props.cohorts 질문 집합별 분모와 결과 건수.
 * @returns 질문 집합 선택 및 기준선·하이브리드 비교.
 */
export function EvaluationComparison({ cohorts }: { cohorts: Cohort[] }) {
  const [key, setKey] = useState('fresh_holdout');
  const cohort = cohorts.find((item) => item.key === key) ?? cohorts[0];
  return (
    <section className="rag-panel" aria-labelledby="rag-comparison-title">
      <div className="rag-panel-heading">
        <div>
          <h2 id="rag-comparison-title">검색 방식 비교</h2>
          <p aria-live="polite">
            총 {cohort.answerable + cohort.unanswerable}건 · 정답 진술 있음 {cohort.answerable}건 ·
            답할 근거 없음 {cohort.unanswerable}건
          </p>
        </div>
        <label className="rag-select">
          평가 세트
          <select value={cohort.key} onChange={(event) => setKey(event.target.value)}>
            {cohorts.map((item) => (
              <option key={item.key} value={item.key}>
                {item.label} {item.answerable + item.unanswerable}건
              </option>
            ))}
          </select>
        </label>
      </div>
      <ul className="rag-legend" aria-label="검색 방식 범례">
        <li><span className="rag-swatch rag-vector" /> E5·ChromaDB</li>
        <li><span className="rag-swatch rag-hybrid" /> Kiwi BM25 결합</li>
      </ul>
      <div className="rag-metric-grid">
        {metricDefinitions.map(({ label, detail }, index) => {
          const total = index === 3 ? cohort.unanswerable : cohort.answerable;
          const vector = cohort.vector[index];
          const hybrid = cohort.hybrid[index];
          const change = hybrid - vector;
          return (
            <article key={label} className="rag-metric">
              <div className="rag-metric-heading">
                <h3>{label}</h3>
                <span className="rag-delta">{change > 0 ? '+' : ''}{change}건</span>
              </div>
              <p>{detail}</p>
              {([
                ['vector', 'E5·ChromaDB', vector],
                ['hybrid', 'Kiwi BM25 결합', hybrid],
              ] as const).map(([kind, method, count]) => (
                <div className="rag-result" key={kind}>
                  <span className="rag-bar" aria-hidden="true">
                    <span className={'rag-' + kind} style={{ width: `${percent(count, total)}%` }} />
                  </span>
                  <span aria-label={`${method} ${total}건 중 ${count}건`}>{count}/{total}</span>
                </div>
              ))}
            </article>
          );
        })}
      </div>
    </section>
  );
}
