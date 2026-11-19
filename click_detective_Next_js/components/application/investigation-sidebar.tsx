import { tabs } from './navigation';
import { ArrowUpRight, ArrowLeft, CheckCheck } from 'lucide-react';
import type { GameState } from '@/app/game/investigation/types';
import type { CaseGameController } from '@/app/game/investigation/use-case-game';

type Props = Omit<Pick<CaseGameController, 'view' | 'state' | 'mobile' | 'navigateTo'>, 'state'> & {
  state: GameState;
};

/** 수사 메뉴와 진행 현황을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.view 현재 선택한 화면 이름.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.mobile 모바일 수사 메뉴가 열려 있는지 여부.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
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
