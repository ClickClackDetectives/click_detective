import { percentile, type Run } from './metrics';

/** 시간을 읽기 쉽게 표시한다.
 * @param value 밀리초 또는 미기록 값.
 * @returns 화면에 표시할 시간.
 */
export function time(value: number | null) {
  return value === null
    ? '미기록'
    : value.toLocaleString('ko-KR', { maximumFractionDigits: 1 }) + ' ms';
}

/** 지정한 실행 집합의 측정값을 집계한다.
 * @param runs 집계할 실행 목록.
 * @returns 화면에 표시할 지표.
 */
export function summarize(runs: Run[]) {
  const measured = runs.filter((run) => run.outcome !== 'fixed');
  const first = measured.filter((run) => run.outcome === 'first').length;
  const fallback = measured.filter((run) => run.outcome === 'fallback').length;
  const known = measured.filter((run) => run.outcome !== 'verified').length;
  return {
    first: known ? Math.round((first / known) * 100) + '%' : '—',
    fallback: measured.length ? Math.round((fallback / measured.length) * 100) + '%' : '—',
    p95: time(
      percentile(
        runs.map((run) => run.elapsed),
        0.95,
      ),
    ),
    median: time(
      percentile(
        runs.map((run) => run.elapsed),
        0.5,
      ),
    ),
  };
}
