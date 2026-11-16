import { Menu, ChevronRight } from 'lucide-react';
import type { CaseGameController } from '../investigation/use-case-game';
import { tabs } from './navigation';
import { InvestigationSidebar } from './investigation-sidebar';
import { BriefingScreen } from '../catalog/briefing-screen';
import { EvidenceScreen } from '../materials/evidence-screen';
import { TestimoniesScreen } from '../testimony/testimonies-screen';
import { InterrogationScreen } from '../interrogation/interrogation-screen';
import { FindingsScreen } from '../findings/findings-screen';
import { InferenceScreen } from '../inference/inference-screen';
import { TimelineScreen } from '../timeline/timeline-screen';
import { NotesScreen } from '../notes/notes-screen';
import { AccusationScreen } from '../accusation/accusation-screen';
import { ResultsScreen } from '../accusation/results-screen';

/** 수사 메뉴와 현재 선택한 작업 화면을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.controller 화면 상태와 사용자 행동 함수 묶음.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function InvestigationWorkspace({ controller }: { controller: CaseGameController }) {
  const {
    view,
    state,
    mobile,
    navigateTo,
    setMobile,
    filter,
    setFilter,
    busy,
    openEvidence,
    updateGame,
    suspect,
    setSuspect,
    currentSuspect,
    scrollEnd,
    attachment,
    setAttachment,
    topicId,
    setTopicId,
    question,
    setQuestion,
    submitQuestion,
    notes,
    setNotes,
    noteStatus,
    setNoteStatus,
    form,
    setForm,
    setModal,
  } = controller;
  if (!state) return null;
  return (
    <div className="workspace">
      <InvestigationSidebar view={view} state={state} mobile={mobile} navigateTo={navigateTo} />
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
        {view === 'briefing' && <BriefingScreen state={state} navigateTo={navigateTo} />}
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
        {view === 'findings' && <FindingsScreen state={state} openEvidence={openEvidence} />}
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
  );
}
