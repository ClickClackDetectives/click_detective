import { Dashboard } from '@/components/agent-dashboard/dashboard';
import { examples } from '@/app/game/agent-dashboard/examples';
import { loadDashboard } from '@/server/diagnostics/dashboard';
import '@/styles/agent-dashboard.css';

export const dynamic = 'force-dynamic';

/** 에이전트 진단 화면에 실측 기록 또는 예시를 전달한다.
 * @returns 에이전트 대시보드 화면.
 */
export default async function AgentDashboardPage() {
  const data = await loadDashboard();
  return (
    <Dashboard runs={data.demo ? examples : data.runs} demo={data.demo} message={data.message} />
  );
}
