import type { Metadata } from 'next';
import { RagDashboard } from '@/components/rag-dashboard/dashboard';
import data from '@/app/game/rag-dashboard/evaluation-data.json';
import type { Evaluation } from '@/app/game/rag-dashboard/metrics';
import '@/styles/rag-dashboard.css';

export const metadata: Metadata = {
  title: 'RAG 개선 대시보드 | 딸깍탐정단',
  description: '자유 심문의 E5·ChromaDB와 Kiwi BM25 평가 결과를 비교합니다.',
};

/** 실제 오프라인 평가 집계값을 RAG 개선 화면에 전달한다.
 * @returns RAG 검색 비교 및 설정 탐색 화면.
 */
export default function RagDashboardPage() {
  return <RagDashboard evaluation={data as Evaluation} />;
}
