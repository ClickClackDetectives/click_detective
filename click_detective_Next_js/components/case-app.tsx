'use client';
import { useCaseGame } from '@/hooks/use-case-game';
import { FindingsScreen } from './screens/findings-screen';
import { InferenceScreen } from './screens/inference-screen';
import { tabs } from './navigation';
import { ArrowUpRight, ChevronRight, X, Menu } from 'lucide-react';
import { HomeScreen } from './screens/home-screen';
import { CasesScreen } from './screens/cases-screen';
import { BriefingScreen } from './screens/briefing-screen';
import { TestimoniesScreen } from './screens/testimonies-screen';
import { EvidenceScreen } from './screens/evidence-screen';
import { InterrogationScreen } from './screens/interrogation-screen';
import { TimelineScreen } from './screens/timeline-screen';
import { NotesScreen } from './screens/notes-screen';
import { AccusationScreen } from './screens/accusation-screen';
import { ResultsScreen } from './screens/results-screen';
import { AppHeader } from './app-header';
import { InvestigationSidebar } from './investigation-sidebar';
import { EvidenceDialog } from './evidence-dialog';
import { GameDialog } from './game-dialog';

/** 앱의 조립도: 상태를 가져와 현재 화면과 공통 UI에 전달한다. */
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
    suspect,
    setSuspect,
    attachment,
    setAttachment,
    question,
    setQuestion,
    topicId,
    setTopicId,
    filter,
    setFilter,
    mobile,
    setMobile,
    notes,
    setNotes,
    noteStatus,
    setNoteStatus,
    form,
    setForm,
    scrollEnd,
    active,
    selectedDoc,
    currentSuspect,
    inProgress,
    updateGame,
    navigateTo,
    startInvestigation,
    openEvidence,
    submitQuestion,
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
      {active && state && (
        <div className="workspace">
          <InvestigationSidebar
            view={view}
            state={state}
            mobile={mobile}
            navigateTo={navigateTo}
          />
          <main className="desk">
            <div className="desk-top">
              <button
                className="mobile-menu"
                aria-label="수사 메뉴 열기"
                onClick={() => setMobile(!mobile)}
              >
                <Menu size={19} />
              </button>
              <div>
                사건 기록 <ChevronRight size={12} /> #0001 <ChevronRight size={12} />
                <span>{tabs.find((t) => t.id === view)?.label ?? '수사 결과'}</span>
              </div>
              <span className="live-status">
                <i />
                {state.verdict ? 'CASE CLOSED' : 'INVESTIGATION IN PROGRESS'}
              </span>
            </div>
            {view === 'briefing' && (
              <BriefingScreen state={state} navigateTo={navigateTo} />
            )}
            {view === 'evidence' && (
              <EvidenceScreen
                state={state}
                filter={filter}
                setFilter={setFilter}
                busy={busy}
                openEvidence={openEvidence}
                updateGame={updateGame}
              />
            )}
            {view === 'testimonies' && (
              <TestimoniesScreen
                state={state}
                busy={busy}
                openEvidence={openEvidence}
                navigateTo={navigateTo}
              />
            )}
            {view === 'interrogate' && (
              <InterrogationScreen
                state={state}
                suspect={suspect}
                setSuspect={setSuspect}
                currentSuspect={currentSuspect}
                busy={busy}
                scrollEnd={scrollEnd}
                attachment={attachment}
                setAttachment={setAttachment}
                topicId={topicId}
                setTopicId={setTopicId}
                question={question}
                setQuestion={setQuestion}
                submitQuestion={submitQuestion}
              />
            )}
            {view === 'findings' && (
              <FindingsScreen state={state} openEvidence={openEvidence} />
            )}
            {view === 'inference' && (
              <InferenceScreen
                state={state}
                busy={busy}
                updateGame={updateGame}
                openEvidence={openEvidence}
                navigateTo={navigateTo}
              />
            )}
            {view === 'timeline' && (
              <TimelineScreen busy={busy} openEvidence={openEvidence} state={state} />
            )}
            {view === 'notes' && (
              <NotesScreen
                state={state}
                notes={notes}
                setNotes={setNotes}
                noteStatus={noteStatus}
                busy={busy}
                updateGame={updateGame}
                setNoteStatus={setNoteStatus}
              />
            )}
            {view === 'accuse' && (
              <AccusationScreen
                state={state}
                form={form}
                setForm={setForm}
                setModal={setModal}
                busy={busy}
                navigateTo={navigateTo}
              />
            )}
            {view === 'results' && state.verdict && (
              <ResultsScreen state={state} setModal={setModal} navigateTo={navigateTo} />
            )}
          </main>
        </div>
      )}
      {!active && (
        <footer>
          <span className="footer-brand">
            열세 번째 종<span>독립 재구현 · 플레이 가능한 데모</span>
          </span>
          <p>
            모든 인물과 사건은 허구입니다. 사용자가 제공한 사건 자료를 기반으로 한 개인
            실습용 데모입니다.
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
