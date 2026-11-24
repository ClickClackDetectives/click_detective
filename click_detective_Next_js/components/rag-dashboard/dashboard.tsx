'use client';

import Link from 'next/link';
import { ArrowLeft, ArrowUpRight } from 'lucide-react';
import type { Evaluation } from '@/app/game/rag-dashboard/metrics';
import { EvaluationComparison } from './evaluation-comparison';
import { SweepPanel } from './sweep-panel';

/** RAG 평가 데이터 출처와 검색 방식·설정별 측정 결과를 표시한다.
 * @param props 오프라인 평가 결과.
 * @param props.evaluation 질문 집합별 성능과 전체 설정 실험.
 * @returns 검색 개선 대시보드.
 */
export function RagDashboard({ evaluation }: { evaluation: Evaluation }) {
  const { defaults, joint, versions } = evaluation;
  return (
    <main className="rag-board">
      <nav className="rag-nav" aria-label="대시보드 이동">
        <Link href="/">
          <ArrowLeft size={15} aria-hidden="true" /> 게임으로
        </Link>
        <Link href="/agent-dashboard">
          에이전트 대시보드 <ArrowUpRight size={15} aria-hidden="true" />
        </Link>
      </nav>
      <header className="rag-header">
        <div>
          <p className="rag-caption">오프라인 평가 · {evaluation.evaluatedOn}</p>
          <h1>RAG 개선 대시보드</h1>
          <p>같은 자유 질문에서 E5·ChromaDB 단독 검색과 Kiwi BM25 재정렬 결과를 비교합니다.</p>
        </div>
        <dl className="rag-defaults" aria-label="게임의 기본 검색 설정">
          <div>
            <dt>E5 / BM25 가중치</dt>
            <dd>{defaults.weight.toFixed(2)} / {(1 - defaults.weight).toFixed(2)}</dd>
          </div>
          <div>
            <dt>최소 유사도 / 1위 차이</dt>
            <dd>{defaults.minimum} / {defaults.gap.toFixed(2)}</dd>
          </div>
          <div>
            <dt>RRF 상수 / 최대 개별 진술</dt>
            <dd>{defaults.rankConstant} / {defaults.topK}개</dd>
          </div>
        </dl>
      </header>

      <EvaluationComparison cohorts={evaluation.comparison} />
      <SweepPanel evaluation={evaluation} />

      <section className="rag-panel" aria-labelledby="rag-joint-title">
        <div className="rag-panel-heading">
          <div>
            <h2 id="rag-joint-title">공동 조정 결과</h2>
            <p>
              유사도·점수 차이·가중치·RRF 상수 {joint.combinations.toLocaleString('ko-KR')}개 조합을
              비교했습니다. 기존 검증 질문 {joint.checkQuestions}건에서 관련 진술 1위 적중은{' '}
              {joint.firstCorrectBefore}/{joint.answerable}건에서 {joint.firstCorrectAfter}/{joint.answerable}건으로
              늘었습니다. 새 검증 질문 {joint.independentQuestions}건에서는 1위 적중률과 오탐률이
              같았습니다.
            </p>
          </div>
        </div>
      </section>

      <footer className="rag-footer">
        <p>
          동일한 질문과 공개 범위에서 최종 선택 진술을 평가했습니다. 검색 지표는 생성된 대사의 품질을
          포함하지 않습니다.
        </p>
        <p>
          multilingual-e5-small · ChromaDB {versions.chromadb} · Kiwi {versions.kiwipiepy} ·
          BM25S {versions.bm25s}
        </p>
      </footer>
    </main>
  );
}
