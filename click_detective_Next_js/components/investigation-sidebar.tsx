import { tabs } from './navigation';
import { ArrowUpRight, ArrowLeft, CheckCheck } from 'lucide-react';
import { type GameState } from '@/lib/case';
import type { CaseGameController } from '@/hooks/use-case-game';

type Props = Omit<
  Pick<CaseGameController, 'view' | 'state' | 'mobile' | 'navigateTo'>,
  'state'
> & { state: GameState };

export function InvestigationSidebar({ view, state, mobile, navigateTo }: Props) {
  return (
    <aside className={'sidebar ' + (mobile ? 'mobile-open' : '')}>
      <div className="sidebar-file">
        <span className="eyebrow">ACTIVE INVESTIGATION</span>
        <h3>THE THIRTEENTH BELL</h3>
        <p>#0001 · 열세 번째 종</p>
        <span className={'badge ' + (state.verdict ? '' : 'green')}>
          {state.verdict
            ? '수사 종결'
            : state.phase === 1
              ? '1차 조사 진행 중'
              : '2차 조사 진행 중'}
        </span>
      </div>
      <nav aria-label="수사 메뉴">
        {tabs.map((t) => (
          <button
            key={t.id}
            className={view === t.id ? 'selected' : ''}
            onClick={() => navigateTo(t.id)}
          >
            <t.icon size={17} />
            {t.label}
            {t.id === 'evidence' && (
              <small>
                {state.ui.physicalReadCount}/{state.ui.physicalCount}
              </small>
            )}
            {t.id === 'findings' && (
              <small
                aria-label={`발견한 쟁점 ${state.progress.counts.findings}개`}
                aria-live="polite"
              >
                {state.progress.counts.findings}개
              </small>
            )}
            {t.id === 'inference' && (
              <small
                aria-label={`확보한 추론 증거 ${state.progress.counts.inference}개`}
                aria-live="polite"
              >
                {state.progress.counts.inference}개
              </small>
            )}
            {t.id === 'accuse' && <ArrowUpRight size={14} />}
          </button>
        ))}
        {state.verdict && (
          <button
            className={view === 'results' ? 'selected' : ''}
            onClick={() => navigateTo('results')}
          >
            <CheckCheck size={17} />
            수사 결과
          </button>
        )}
      </nav>
      <button className="sidebar-exit" onClick={() => navigateTo('cases')}>
        <ArrowLeft size={15} /> 사건 기록실로
      </button>
    </aside>
  );
}
