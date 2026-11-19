export type Stage = 'retrieval' | 'generation' | 'verification';
export type Outcome = 'first' | 'retried' | 'verified' | 'fallback' | 'fixed' | 'error';
export type Run = {
  evaluation?: { rouge1?: number; rouge2?: number; rougeL?: number };
  experiment?: {
    rag?: boolean;
    embedding?: boolean;
    chunking?: boolean;
    ragVersion?: string;
    generationVersion?: string;
    model?: string;
    qlora?: boolean;
    qloraInferred?: boolean;
  };
  label: string;
  version: string;
  mode: string;
  elapsed: number | null;
  outcome: Outcome;
  events: {
    stage: Stage | 'candidate_rejected' | 'failure';
    ms: number | null;
    selected?: number;
    relevanceMean?: number;
    relevanceMax?: number;
    approved?: number;
    required?: number;
    code?: string;
  }[];
  example?: { question: string; candidates: string[]; answer: string };
};

export const stageNames: Record<Stage, string> = {
  retrieval: '전처리',
  generation: '생성',
  verification: '검증',
};
export const outcomeNames: Record<Outcome, string> = {
  first: '첫 후보 통과',
  retried: '재생성 후 통과',
  verified: '검증 통과 · 시도 미확인',
  fallback: '승인 원문 복구',
  fixed: '고정 답변',
  error: '오류',
};

/** 측정값에서 지정한 백분위의 시간을 구한다.
 * @param values 측정 시간 목록.
 * @param fraction 백분위 비율.
 * @returns 시간 또는 측정값이 없으면 null.
 */
export function percentile(values: (number | null)[], fraction: number) {
  const sorted = values.filter((value): value is number => value !== null).sort((a, b) => a - b);
  return sorted[Math.max(0, Math.ceil(sorted.length * fraction) - 1)] ?? null;
}

/** 한 실행의 같은 단계에서 기록된 시간을 합산한다.
 * @param run 심문 진단 한 건.
 * @param stage 합산할 단계.
 * @returns 기록된 시간 합계 또는 측정값이 없으면 null.
 */
export function stageTime(run: Run, stage: Stage) {
  const times = run.events.filter((event) => event.stage === stage && event.ms !== null);
  return times.length ? times.reduce((sum, event) => sum + (event.ms ?? 0), 0) : null;
}
