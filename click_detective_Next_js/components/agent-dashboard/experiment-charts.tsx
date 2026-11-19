import { Bars } from './metric-bars';
import { useState } from 'react';
import { experimentExamples } from '@/app/game/agent-dashboard/experiment-examples';
import { percentile, stageTime, type Run } from '@/app/game/agent-dashboard/metrics';

type Experiment = NonNullable<Run['experiment']>;
type Group = { name: string; runs: Run[] };
type Chart = { title: string; group: (config: Experiment) => string | undefined };
const retrievalCharts: Chart[] = [
  {
    title: 'RAG 사용 여부',
    group: (c) => (c.rag === undefined ? undefined : c.rag ? 'RAG 켬' : 'RAG 끔'),
  },
  {
    title: '임베딩·청킹 구성별',
    group: (c) =>
      c.rag !== true || c.embedding === undefined || c.chunking === undefined
        ? undefined
        : `임베딩 ${c.embedding ? '켬' : '끔'} · 청킹 ${c.chunking ? '켬' : '끔'}`,
  },
  { title: 'RAG 버전별', group: (c) => (c.rag === true ? c.ragVersion : undefined) },
];
const generationCharts: Chart[] = [
  { title: '모델별 생성 성능', group: (c) => c.model },
  {
    title: '같은 모델의 QLoRA 비교',
    group: (c) =>
      c.model && c.qlora !== undefined ? `${c.model} · QLoRA ${c.qlora ? '켬' : '끔'}` : undefined,
  },
  { title: '대사 생성 버전별', group: (c) => c.generationVersion },
];

/** 설정을 확인할 수 있는 실행을 그래프 그룹으로 묶는다.
 * @param runs 실행 기록.
 * @param chart 비교 기준.
 * @param stage 비교할 에이전트.
 * @returns 그룹별 실행 기록.
 */
function groupRuns(runs: Run[], chart: Chart, stage: 'retrieval' | 'generation'): Group[] {
  const groups = new Map<string, Run[]>();
  for (const run of runs) {
    if (!run.experiment || !run.events.some((event) => event.stage === stage)) continue;
    const name = chart.group(run.experiment);
    if (!name) continue;
    const group = groups.get(name) ?? [];
    group.push(run);
    groups.set(name, group);
  }
  if (chart.title === '같은 모델의 QLoRA 비교') {
    for (const name of groups.keys()) {
      const other = name.endsWith('켬') ? name.slice(0, -1) + '끔' : name.slice(0, -1) + '켬';
      if (!groups.has(other)) groups.delete(name);
    }
  }
  return [...groups].map(([name, items]) => ({ name, runs: items }));
}

/** 그룹별 측정값의 중앙값과 표본 수를 구한다.
 * @param groups 비교 그룹.
 * @param measure 실행 한 건에서 읽을 측정값.
 * @returns 그래프 값과 유효 표본 수.
 */
function medians(groups: Group[], measure: (run: Run) => number | undefined) {
  return groups.map(({ name, runs }) => {
    const values = runs.map((run) => measure(run) ?? null);
    return {
      name,
      value: percentile(values, 0.5),
      count: values.filter((value) => value !== null).length,
    };
  });
}

const rougeMetrics = [
  { key: 'rouge1', label: 'ROUGE-1 F1 중앙값' },
  { key: 'rouge2', label: 'ROUGE-2 F1 중앙값' },
  { key: 'rougeL', label: 'ROUGE-L F1 중앙값' },
] as const;

/** 선택한 에이전트의 실험 비교를 표시한다.
 * @param props 현재 실행과 단계.
 * @param props.runs 선택한 실행 모드의 기록.
 * @param props.stage 비교할 에이전트.
 * @returns 실제 또는 예시 비교 그래프.
 */
export function ExperimentCharts({
  runs,
  stage,
}: {
  runs: Run[];
  stage: 'retrieval' | 'generation';
}) {
  const charts = stage === 'retrieval' ? retrievalCharts : generationCharts;
  const [selection, setSelection] = useState(0);
  return (
    <div className="agent-experiments">
      <nav className="agent-controls agent-tabs" aria-label="비교 기준">
        {charts.map(({ title }, index) => (
          <button
            type="button"
            key={title}
            aria-pressed={selection === index}
            onClick={() => setSelection(index)}
          >
            {title}
          </button>
        ))}
      </nav>
      {stage === 'retrieval' ? (
        <p>
          관련성 점수는 검색기가 부여한 값입니다. 검색을 끈 실행은 미기록으로 표시하며, 점수 체계가
          같을 때 비교하세요.
        </p>
      ) : (
        <p>
          ROUGE는 기준 답변과 겹치는 표현을 측정합니다. 기준 답변 평가 기록이 없는 실행은 미기록으로
          표시합니다.
        </p>
      )}
      <p>관측값 비교입니다. 개선 효과를 보려면 동일한 질문·수사 상태·실행 환경에서 비교하세요.</p>
      {charts.slice(selection, selection + 1).map((chart) => {
        const actual = groupRuns(runs, chart, stage);
        const isExample = actual.length < 2;
        const groups = isExample ? groupRuns(experimentExamples, chart, stage) : actual;
        const duration = groups.map(({ name, runs: items }) => {
          const values = items.map((item) => stageTime(item, stage));
          return {
            name,
            value: percentile(values, 0.5),
            count: values.filter((v) => v !== null).length,
          };
        });
        const quality = groups.map(({ name, runs: items }) => {
          if (stage === 'retrieval') {
            const values = items.map(
              (item) => item.events.find((event) => event.stage === 'retrieval')?.selected ?? null,
            );
            return {
              name,
              value: percentile(values, 0.5),
              count: values.filter((v) => v !== null).length,
            };
          }
          const known = items.filter(
            (item) =>
              item.outcome !== 'fixed' &&
              item.outcome !== 'verified' &&
              (chart.title !== '같은 모델의 QLoRA 비교' || !item.experiment?.qloraInferred),
          );
          const first = known.filter((item) => item.outcome === 'first').length;
          return {
            name,
            value: known.length ? (first / known.length) * 100 : null,
            count: known.length,
          };
        });
        return (
          <article key={chart.title} className="agent-experiment">
            <h3>
              {chart.title} · {isExample ? '예시 데이터' : '실측 데이터'}
            </h3>
            {isExample && <p>비교 가능한 실측 그룹 {actual.length}개. 가상 수치로 표시합니다.</p>}
            <Bars label="단계 시간 중앙값" values={duration} unit=" ms" />
            <Bars
              label={stage === 'retrieval' ? '선택 사실 수 중앙값' : '첫 후보 통과율'}
              values={quality}
              unit={stage === 'retrieval' ? '개' : '%'}
            />
            {stage === 'retrieval' ? (
              <>
                <Bars
                  label="관련성 평균 점수의 중앙값"
                  values={medians(
                    groups,
                    (run) => run.events.find((event) => event.stage === 'retrieval')?.relevanceMean,
                  )}
                  unit="점"
                />
                <Bars
                  label="최고 관련성 점수의 중앙값"
                  values={medians(
                    groups,
                    (run) => run.events.find((event) => event.stage === 'retrieval')?.relevanceMax,
                  )}
                  unit="점"
                />
              </>
            ) : (
              <>
                {rougeMetrics.map(({ key, label }) => (
                  <Bars
                    key={key}
                    label={label}
                    values={medians(groups, (run) => {
                      const score = run.evaluation?.[key];
                      return score === undefined ? undefined : score * 100;
                    })}
                    unit="%"
                  />
                ))}
                <Bars
                  label="생성 시간 p95"
                  values={groups.map(({ name, runs: items }) => {
                    const values = items.map((run) => stageTime(run, 'generation'));
                    return {
                      name,
                      value: percentile(values, 0.95),
                      count: values.filter((value) => value !== null).length,
                    };
                  })}
                  unit=" ms"
                />
              </>
            )}
          </article>
        );
      })}
    </div>
  );
}
