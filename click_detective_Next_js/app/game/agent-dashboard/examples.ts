import type { Run } from './metrics';

const question = '그날 밤 몇 시에 복도를 지나갔나요?';
const answer = '22시 40분에 복도를 지나갔어요.';

export const examples: Run[] = [
  {
    label: '예시 질문 1 · 개선 후',
    version: '예시 개선 후',
    mode: 'demo',
    elapsed: 870,
    experiment: { model: '가상 모델 B' },
    outcome: 'first',
    events: [
      { stage: 'retrieval', ms: 15, approved: 3, selected: 2, required: 1 },
      { stage: 'generation', ms: 530 },
      { stage: 'verification', ms: 290 },
    ],
    example: { question, candidates: [answer], answer },
  },
  {
    label: '예시 질문 1 · 개선 전',
    version: '예시 개선 전',
    mode: 'demo',
    elapsed: 1860,
    experiment: { model: '가상 모델 A' },
    outcome: 'retried',
    events: [
      { stage: 'retrieval', ms: 18, approved: 3, selected: 2, required: 1 },
      { stage: 'generation', ms: 530 },
      { stage: 'verification', ms: 330 },
      { stage: 'candidate_rejected', ms: null, code: 'missing_time' },
      { stage: 'generation', ms: 535 },
      { stage: 'verification', ms: 380 },
    ],
    example: { question, candidates: ['늦은 밤에 복도를 지나갔어요.', answer], answer },
  },
];
