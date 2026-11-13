import { Fingerprint } from 'lucide-react';

import type { CaseGameController } from '@/hooks/use-case-game';

type Props = Pick<
  CaseGameController,
  'view' | 'state' | 'inProgress' | 'navigateTo' | 'setModal'
>;

export function AppHeader({ view, state, inProgress, navigateTo, setModal }: Props) {
  return (
    <header className="topbar">
      <button
        className="brand"
        onClick={() => navigateTo('home')}
        aria-label="딸깍탐정단 홈"
      >
        <span className="brand-mark">
          <Fingerprint size={25} aria-hidden="true" />
        </span>
        <span>
          딸깍<span className="brand-zero">탐정단</span>
          <small>CLICK DETECTIVE CLUB</small>
        </span>
      </button>
      <nav aria-label="주 메뉴">
        <button
          className={view === 'cases' ? 'active-link' : ''}
          onClick={() => navigateTo('cases')}
        >
          사건 기록
        </button>
        <button
          onClick={() =>
            state
              ? navigateTo(state.verdict ? 'results' : 'briefing')
              : setModal('record')
          }
        >
          내 수사 기록{inProgress && <i className="live-dot" />}
        </button>
      </nav>
      <div className="top-right">
        <span className="edition">INTERACTIVE DETECTIVE EXPERIENCE</span>
        <button className="outline small" onClick={() => setModal('about')}>
          <Fingerprint size={15} /> 데모 안내
        </button>
      </div>
    </header>
  );
}
