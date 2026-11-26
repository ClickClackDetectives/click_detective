import { useState } from 'react';
import { metricDefinitions, percent, sweepSeries, type Evaluation } from '@/app/game/rag-dashboard/metrics';
import { SweepChart } from './sweep-chart';

/** 유사도와 가중치 실험의 측정값을 조작해 볼 수 있게 표시한다.
 * @param props 실험 기록과 질문 표본 정보.
 * @param props.evaluation 임계값과 RRF 실험 집계.
 * @returns 설정 선택, 성능 그래프와 현재 선택의 원시 건수.
 */
export function SweepPanel({ evaluation }: { evaluation: Evaluation }) {
  const { axes, defaults } = evaluation;
  const [mode, setMode] = useState<'threshold' | 'weight'>('threshold');
  const [minimumIndex, setMinimumIndex] = useState(axes.thresholds.indexOf(defaults.minimum));
  const [gap, setGap] = useState(defaults.gap);
  const [weight, setWeight] = useState(Math.round(defaults.weight * 100));
  const [rankConstant, setRankConstant] = useState(defaults.rankConstant);
  const cohort = evaluation.comparison.find((item) => item.key === 'tuning') ?? evaluation.comparison[0];
  const weights = mode === 'weight';
  const sweep = weights ? evaluation.weightSweep : evaluation.thresholdSweep;
  const points = sweepSeries(sweep, weights ? rankConstant : gap, cohort);
  const setting = weights ? weight / 100 : axes.thresholds[minimumIndex];
  const selected = points.find((point) => point.setting === setting);
  const rangeValue = weights ? weight : minimumIndex;
  const rangeText = weights ? `${weight}%` : String(setting);
  return (
    <section className="rag-panel" aria-labelledby="rag-sweep-title">
      <div className="rag-panel-heading">
        <div>
          <h2 id="rag-sweep-title">설정별 성능 탐색</h2>
          <p>설정 선택 질문 {cohort.answerable + cohort.unanswerable}건에서 측정한 {sweep.length.toLocaleString('ko-KR')}개 조합</p>
        </div>
        <div className="rag-segments" role="group" aria-label="실험 종류">
          <button type="button" aria-pressed={!weights} onClick={() => setMode('threshold')}>
            유사도 기준
          </button>
          <button type="button" aria-pressed={weights} onClick={() => setMode('weight')}>
            RRF 가중치
          </button>
        </div>
      </div>
      <p className="rag-experiment-note">
        {weights
          ? `유사도 ${defaults.minimum}, 1위와의 차이 ${defaults.gap.toFixed(2)}를 고정하고 통과한 후보의 순서를 비교합니다.`
          : 'E5·ChromaDB 단독 검색에서 최소 유사도와 1위 점수 차이를 바꿔 비교한 결과입니다.'}
        {' '}이 화면의 선택은 게임 설정에 영향을 주지 않습니다.
      </p>
      <div className="rag-tuning-controls">
        <label className="rag-range">
          <span>
            {weights ? 'E5 가중치' : '최소 유사도'}
            <strong>{weights ? `E5 ${rangeText} · BM25 ${100 - weight}%` : rangeText}</strong>
          </span>
          <input
            type="range"
            aria-label={weights ? 'E5 가중치' : '최소 유사도'}
            aria-valuetext={rangeText}
            min={0}
            max={weights ? 100 : axes.thresholds.length - 1}
            value={rangeValue}
            onChange={(event) => {
              const value = event.target.valueAsNumber;
              if (weights) setWeight(value);
              else setMinimumIndex(value);
            }}
          />
          <span className="rag-range-ends" aria-hidden="true">
            <span>{weights ? '0%' : axes.thresholds[0]}</span>
            <span>{weights ? '100%' : axes.thresholds.at(-1)}</span>
          </span>
        </label>
        {weights ? (
          <label className="rag-select">
            RRF 상수
            <select value={rankConstant} onChange={(event) => setRankConstant(Number(event.target.value))}>
              {axes.rankConstants.map((value) => <option key={value}>{value}</option>)}
            </select>
          </label>
        ) : (
          <label className="rag-select">
            1위와의 최대 차이
            <select value={gap} onChange={(event) => setGap(Number(event.target.value))}>
              {axes.gaps.map((value) => <option key={value} value={value}>{value.toFixed(4)}</option>)}
            </select>
          </label>
        )}
      </div>
      <SweepChart points={points} selected={setting} weights={weights} />
      {selected && (
        <dl className="rag-sweep-results" aria-label="선택한 설정의 측정값" aria-live="polite">
          {metricDefinitions.map(({ label }, index) => {
            const total = index === 3 ? cohort.unanswerable : cohort.answerable;
            const count = selected.counts[index];
            return (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{count}/{total} <small>{percent(count, total)}%</small></dd>
              </div>
            );
          })}
        </dl>
      )}
    </section>
  );
}
