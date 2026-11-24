export const metricDefinitions = [
  { label: '관련 진술이 1위', detail: '정답 진술이 있는 질문 중 첫 번째 진술이 관련 있었던 비율' },
  { label: '필요한 진술 모두 선택', detail: '정답 진술이 있는 질문 중 필요한 진술을 모두 찾은 비율' },
  { label: '필요한 진술만 선택', detail: '정답 진술이 있는 질문 중 필요한 진술만 정확히 찾은 비율' },
  { label: '근거 없는 질문에 오탐', detail: '정답 진술이 없는 질문 중 진술을 한 건 이상 선택한 비율' },
] as const;

export type MetricCounts = [first: number, complete: number, exact: number, falseMatch: number];
export type SweepRow = [setting: number, group: number, ...counts: MetricCounts];

export type Cohort = {
  key: string;
  label: string;
  answerable: number;
  unanswerable: number;
  vector: MetricCounts;
  hybrid: MetricCounts;
};

export type Evaluation = {
  evaluatedOn: string;
  versions: { chromadb: string; kiwipiepy: string; bm25s: string };
  comparison: Cohort[];
  defaults: { minimum: number; gap: number; topK: number; weight: number; rankConstant: number };
  joint: {
    combinations: number;
    checkQuestions: number;
    firstCorrectBefore: number;
    firstCorrectAfter: number;
    answerable: number;
    independentQuestions: number;
  };
  axes: { thresholds: number[]; gaps: number[]; rankConstants: number[] };
  thresholdSweep: SweepRow[];
  weightSweep: SweepRow[];
};

/** 표본 수를 기준으로 차트에 표시할 비율을 계산한다.
 * @param count 해당 조건에 맞은 질문 수.
 * @param total 지표에 해당하는 전체 질문 수.
 * @returns 소수점 첫째 자리까지 반올림한 백분율.
 */
export function percent(count: number, total: number) {
  return Math.round((count / total) * 1000) / 10;
}

/** 선택한 보조 설정으로 측정한 행에서 각 지표의 비율을 구한다.
 * @param rows 해당 실험의 전체 측정 행.
 * @param group 고정할 1위와의 차이 또는 RRF 상수.
 * @param cohort 설정 선택에 사용한 질문 집합.
 * @returns 차트와 현재 설정 표에 쓰는 지표 목록.
 */
export function sweepSeries(rows: SweepRow[], group: number, cohort: Cohort) {
  return rows.filter((row) => row[1] === group).map(([setting, , ...counts]) => ({
    setting,
    counts,
    first: percent(counts[0], cohort.answerable),
    complete: percent(counts[1], cohort.answerable),
    exact: percent(counts[2], cohort.answerable),
    falseMatch: percent(counts[3], cohort.unanswerable),
  }));
}

export type SweepPoint = ReturnType<typeof sweepSeries>[number];
