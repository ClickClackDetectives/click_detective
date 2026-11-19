'use client';

import { ExperimentCharts } from './experiment-charts';
import { OutcomeChart, ModelResponseChart } from './run-charts';
import { Comparison } from './comparison';
import { summarize, time } from '@/app/game/agent-dashboard/summary';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import {
  outcomeNames,
  percentile,
  stageNames,
  stageTime,
  type Run,
  type Stage,
} from '@/app/game/agent-dashboard/metrics';

const tabs = [
  ['summary', '전체 요약'],
  ['trend', '모델별 응답 시간'],
  ['retrieval', '전처리 · RAG'],
  ['generation', '대사 생성'],
  ['verification', '검증'],
  ['detail', '심문 상세'],
  ['comparison', '버전 비교'],
] as const;
type Tab = (typeof tabs)[number][0];

/** 진단 기록과 예시를 같은 화면에 표시한다.
 * @param props 실행 목록과 데이터 출처 안내.
 * @param props.runs 표시할 실행 목록.
 * @param props.demo 예시 여부.
 * @param props.message 연결 상태 안내.
 * @returns 단계별 지표 및 실행 상세 화면.
 */
export function Dashboard({
  runs,
  demo,
  message,
}: {
  runs: Run[];
  demo: boolean;
  message: string;
}) {
  const router = useRouter();
  const [mode, setMode] = useState('');
  const [tab, setTab] = useState<Tab>('summary');
  const stage: Stage | null =
    tab === 'retrieval' || tab === 'generation' || tab === 'verification' ? tab : null;
  const [selected, setSelected] = useState('');
  const modes = [...new Set(runs.map((run) => run.mode))];
  const activeMode = modes.includes(mode) ? mode : modes[0];
  const visible = runs.filter((run) => run.mode === activeMode);
  const run = visible.find((item) => item.label === selected) ?? visible[0];
  const stats = summarize(visible);
  const counts = Object.entries(outcomeNames).map(([key, label]) => ({
    label,
    count: visible.filter((item) => item.outcome === key).length,
  }));
  const rejections = visible
    .flatMap((item) => item.events)
    .filter((event) => event.stage === 'candidate_rejected');
  const rejectionCodes = [...new Set(rejections.map((event) => event.code ?? '미기록'))];
  return (
    <main className="agent-board">
      <header>
        <Link href="/">← 게임으로</Link>
        <h1>에이전트 대시보드</h1>
        <p role="status">
          <strong>{demo ? '예시 데이터' : '실측 데이터'}</strong> · {message}
        </p>
        <div className="agent-controls">
          <button onClick={() => router.refresh()}>연결 및 기록 다시 확인</button>
          <label>
            실행 모드{' '}
            <select value={activeMode} onChange={(event) => setMode(event.target.value)}>
              {modes.map((value) => (
                <option key={value}>{value}</option>
              ))}
            </select>
          </label>
        </div>
      </header>
      <nav className="agent-controls agent-tabs" aria-label="대시보드 분류">
        {tabs.map(([key, label]) => (
          <button key={key} type="button" aria-pressed={tab === key} onClick={() => setTab(key)}>
            {label}
          </button>
        ))}
      </nav>
      {tab === 'summary' && (
        <section aria-labelledby="summary-title">
          <h2 id="summary-title">전체 요약 · {visible.length}건</h2>
          <dl className="agent-cards">
            <div>
              <dt>첫 후보 통과율</dt>
              <dd>{stats.first}</dd>
            </div>
            <div>
              <dt>복구율</dt>
              <dd>{stats.fallback}</dd>
            </div>
            <div>
              <dt>응답 시간 중앙값</dt>
              <dd>{stats.median}</dd>
            </div>
            <div>
              <dt>응답 시간 p95</dt>
              <dd>{stats.p95}</dd>
            </div>
          </dl>
          <p>
            통과율의 분모는 고정 답변과 시도를 확인할 수 없는 통과 건을 제외한 실행입니다. 복구율은
            고정 답변을 제외합니다.
          </p>
          <OutcomeChart counts={counts} />
        </section>
      )}
      {tab === 'trend' && <ModelResponseChart runs={visible} />}
      {stage && (
        <section aria-labelledby="stage-title">
          <h2 id="stage-title">{stageNames[stage]} 기록</h2>
          <p>
            기록된 호출 시간 합계의 요청별 중앙값{' '}
            <strong>
              {time(
                percentile(
                  visible.map((item) => stageTime(item, stage)),
                  0.5,
                ),
              )}
            </strong>
          </p>
          {stage === 'retrieval' && (
            <p>
              선택·승인·필수 사실 수는 아래 실행 상세에서 확인할 수 있습니다. 필수 사실의 보존
              여부를 판정하려면 추가 기록이 필요합니다.
            </p>
          )}
          {stage === 'generation' && (
            <p>
              기록된 생성 호출{' '}
              {
                visible
                  .flatMap((item) => item.events)
                  .filter((event) => event.stage === 'generation').length
              }
              회
            </p>
          )}
          {stage !== 'verification' && (
            <ExperimentCharts key={stage} runs={demo ? [] : visible} stage={stage} />
          )}
          {stage === 'verification' && (
            <ul>
              {rejectionCodes.length ? (
                rejectionCodes.map((code) => (
                  <li key={code}>
                    {code} ·{' '}
                    {rejections.filter((event) => (event.code ?? '미기록') === code).length}건
                  </li>
                ))
              ) : (
                <li>기록된 후보 거절 사유가 없습니다.</li>
              )}
            </ul>
          )}
        </section>
      )}
      {tab === 'detail' && run && (
        <section aria-labelledby="run-title">
          <h2 id="run-title">심문 한 건 상세</h2>
          <label>
            실행 선택{' '}
            <select value={run.label} onChange={(event) => setSelected(event.target.value)}>
              {visible.map((item) => (
                <option key={item.label} value={item.label}>
                  {item.label} · {outcomeNames[item.outcome]}
                </option>
              ))}
            </select>
          </label>
          <p>
            {run.version} · {outcomeNames[run.outcome]} · {time(run.elapsed)}
          </p>
          {run.example && (
            <>
              <p>{run.example.question}</p>
              <ol>
                {run.example.candidates.map((candidate, index) => (
                  <li key={index}>{candidate}</li>
                ))}
              </ol>
              <p>최종 답변 · {run.example.answer}</p>
            </>
          )}
          {!demo && <p>실측 진단 로그는 질문과 대사 원문을 저장하지 않습니다.</p>}
          <ol>
            {run.events.map((event, index) => (
              <li key={index}>
                {event.stage === 'candidate_rejected'
                  ? '후보 거절'
                  : event.stage === 'failure'
                    ? '실패 처리'
                    : stageNames[event.stage]}
                {' · '}
                {time(event.ms)}
                {event.code && ' · ' + event.code}
                {event.stage === 'retrieval' &&
                  ` · 승인 ${event.approved ?? '—'} / 선택 ${event.selected ?? '—'} / 필수 ${event.required ?? '—'}`}
              </li>
            ))}
          </ol>
        </section>
      )}
      {tab === 'comparison' && <Comparison runs={visible} demo={demo} />}
    </main>
  );
}
