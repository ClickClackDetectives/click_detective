'use client';
import { ArrowUpRight, X } from 'lucide-react';
import { useCaseGame } from '../investigation/use-case-game';
import { HomeScreen } from '../catalog/home-screen';
import { CasesScreen } from '../catalog/cases-screen';
import { AppHeader } from './app-header';
import { EvidenceDialog } from '../materials/evidence-dialog';
import { GameDialog } from './game-dialog';
import { InvestigationWorkspace } from './investigation-workspace';

/** 앱의 조립도: 상태를 가져와 현재 화면과 공통 UI에 전달한다.
 * 파라미터 없음.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export default function CaseApp() {
  const controller = useCaseGame();
  const {
    view,
    state,
    ready,
    busy,
    error,
    setError,
    modal,
    setModal,
    setDoc,
    setAttachment,
    active,
    selectedDoc,
    inProgress,
    updateGame,
    navigateTo,
    startInvestigation,
    form,
  } = controller;
  return (
    <div className={active ? 'app investigation' : 'app'}>
      <AppHeader
        view={view}
        state={state}
        inProgress={inProgress}
        navigateTo={navigateTo}
        setModal={setModal}
      />
      {error && (
        <div className="error-toast" role="alert">
          {error}
          <button onClick={() => setError('')} aria-label="오류 닫기">
            <X size={16} />
          </button>
        </div>
      )}
      {view === 'home' && (
        <HomeScreen
          busy={busy}
          ready={ready}
          inProgress={inProgress}
          startInvestigation={startInvestigation}
          navigateTo={navigateTo}
        />
      )}
      {view === 'cases' && (
        <CasesScreen
          busy={busy}
          ready={ready}
          inProgress={inProgress}
          startInvestigation={startInvestigation}
          setModal={setModal}
        />
      )}
      {active && state && <InvestigationWorkspace controller={controller} />}
      {!active && (
        <footer>
          <span className="footer-brand">
            열세 번째 종<span>독립 재구현 · 플레이 가능한 데모</span>
          </span>
          <p>
            모든 인물과 사건은 허구입니다. 사용자가 제공한 사건 자료를 기반으로 한 개인 실습용
            데모입니다.
          </p>
          <button onClick={() => setModal('about')}>
            프로젝트 안내 <ArrowUpRight size={13} />
          </button>
        </footer>
      )}
      {selectedDoc && (
        <EvidenceDialog
          selectedDoc={selectedDoc}
          setDoc={setDoc}
          setAttachment={setAttachment}
          navigateTo={navigateTo}
        />
      )}
      {modal && (
        <GameDialog
          modal={modal}
          busy={busy}
          setModal={setModal}
          updateGame={updateGame}
          form={form}
          navigateTo={navigateTo}
          startInvestigation={startInvestigation}
        />
      )}
    </div>
  );
}
