import test from 'node:test';
import assert from 'node:assert/strict';
import data from '../app/game/rag-dashboard/evaluation-data.json' with { type: 'json' };
import { sweepSeries, type Evaluation } from '../app/game/rag-dashboard/metrics.ts';

const evaluation = data as Evaluation;

test('RAG 대시보드는 새 검증 질문의 동일한 분모에서 검색 방식을 비교한다', () => {
  const fresh = evaluation.comparison.find((item) => item.key === 'fresh_holdout');
  assert.ok(fresh);
  assert.equal(fresh.answerable, 35);
  assert.equal(fresh.unanswerable, 15);
  assert.deepEqual(fresh.vector, [17, 18, 8, 2]);
  assert.deepEqual(fresh.hybrid, [24, 19, 8, 2]);
  const independent = evaluation.comparison.find((item) => item.key === 'joint_holdout');
  assert.deepEqual(independent?.vector, [21, 21, 12, 4]);
  assert.deepEqual(independent?.hybrid, [24, 21, 12, 4]);
});

test('기본 설정과 일치하는 임계값 및 RRF 측정값을 각각 선택한다', () => {
  const { defaults, axes } = evaluation;
  assert.equal(defaults.rankConstant, 40);
  const cohort = evaluation.comparison.find((item) => item.key === 'tuning');
  assert.ok(cohort);
  assert.equal(evaluation.thresholdSweep.length, 1300);
  assert.equal(evaluation.weightSweep.length, 1313);
  const threshold = sweepSeries(evaluation.thresholdSweep, defaults.gap, cohort);
  const weights = sweepSeries(evaluation.weightSweep, defaults.rankConstant, cohort);
  assert.equal(threshold.length, axes.thresholds.length);
  assert.equal(weights.length, 101);
  assert.deepEqual(threshold.find((point) => point.setting === defaults.minimum)?.counts, cohort.vector);
  assert.deepEqual(weights.find((point) => point.setting === defaults.weight)?.counts, cohort.hybrid);
  assert.equal(threshold.find((point) => point.setting === defaults.minimum)?.falseMatch, 41);
});
