import { Fingerprint } from 'lucide-react';

import type { CaseGameController } from '@/app/game/investigation/use-case-game';

import { BgmToggle } from './bgm-toggle';
import { AccountControls } from '../auth/account-controls';

type Props = Pick<
  CaseGameController,
  'view' | 'state' | 'inProgress' | 'navigateTo' | 'setModal' | 'requireLogin'
>;

/** 현재 화면에 맞는 상단 메뉴를 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.view 현재 선택한 화면 이름.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.inProgress 진행 중인 수사가 있으면 해당 상태, 없으면 null 또는 false.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @param props.setModal 안내 팝업을 열거나 닫는 함수.
 * @param props.requireLogin 수사 진입 전에 로그인 여부를 확인하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function AppHeader({ view, state, inProgress, navigateTo, setModal, requireLogin }: Props) {
  return (
    <header className="topbar">
      <button className="brand" onClick={() => navigateTo('home')} aria-label="딸깍탐정단 홈">
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
          onClick={() => {
            if (!requireLogin()) return;
            if (state) navigateTo(state.verdict ? 'results' : 'briefing');
            else setModal('record');
          }}
        >
          내 수사 기록{inProgress && <i className="live-dot" />}
        </button>
      </nav>
      <div className="top-right">
        <span className="edition">INTERACTIVE DETECTIVE EXPERIENCE</span>
        <BgmToggle />
        <AccountControls />
      </div>
    </header>
  );
}
