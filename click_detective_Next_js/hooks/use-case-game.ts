'use client';
import { useEffect, useRef, useState } from 'react';
import { suspects, type GameState, type SuspectId } from '@/lib/case';
import type { InvestigationDocument } from '@/lib/investigation-documents';
import { requestGame, requestDocument, currentGame } from '@/lib/game-client';
import type { View } from '@/components/navigation';
import { bgm } from '@/lib/bgm';

/** 화면 상태와 서버 요청을 연결한다. 화면 마크업은 components/screens에 있다. */
export function useCaseGame() {
  // 화면에만 필요한 상태: 메뉴·입력·팝업. 서버 저장 기록(state)과 분리한다.
  const [view, setView] = useState<View>('home');
  const [state, setState] = useState<GameState | null>(null);
  const [selectedDoc, setSelectedDoc] = useState<InvestigationDocument>();
  const actionLock = useRef(false);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [modal, setModal] = useState<string | null>(null);
  const [doc, setDoc] = useState<string | null>(null);
  const [suspect, setSuspect] = useState<SuspectId>('yoon');
  const [attachment, setAttachment] = useState('');
  const [question, setQuestion] = useState('');
  const [topicId, setTopicId] = useState('');
  const [filter, setFilter] = useState('');
  const [mobile, setMobile] = useState(false);
  const [notes, setNotes] = useState('');
  const [noteStatus, setNoteStatus] = useState('저장됨');
  const [form, setForm] = useState({
    suspectId: '',
    motive: '',
    method: '',
    evidenceIds: [] as string[],
  });
  const scrollEnd = useRef<HTMLDivElement>(null);
  const stateRef = useRef(state);
  stateRef.current = state;
  const latestNotes = useRef(notes);
  latestNotes.current = notes;
  const active = state !== null && view !== 'home' && view !== 'cases';
  // 처음 열 때 쿠키에 연결된 수사 기록을 복원한다.
  useEffect(() => {
    let alive = true;
    requestGame('state')
      .then((savedState) => {
        if (alive) {
          setState(savedState);
          setNotes(savedState?.notes ?? '');
        }
      })
      .catch(() => {
        if (alive)
          setError(
            '기존 수사 기록을 불러오지 못했습니다. 새로고침 후 다시 시도하세요.',
          );
      })
      .finally(() => {
        if (alive) setReady(true);
      });
    return () => {
      alive = false;
    };
  }, []);
  useEffect(() => {
    scrollEnd.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [state?.messages.length]);
  useEffect(() => {
    if (!doc) setSelectedDoc(undefined);
    if (!modal && !doc) return;
    const previous = document.activeElement as HTMLElement | null;
    const old = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !busy) {
        setModal(null);
        setDoc(null);
      }
      if (e.key === 'Tab') {
        const dialog = document.querySelector('[role="dialog"]');
        const items = dialog?.querySelectorAll<HTMLElement>(
          'button:not(:disabled),select:not(:disabled),input:not(:disabled),textarea:not(:disabled),[tabindex="0"]',
        );
        if (!items?.length) return;
        const first = items[0],
          last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };
    document.addEventListener('keydown', handler);
    return () => {
      document.body.style.overflow = old;
      document.removeEventListener('keydown', handler);
      previous?.focus();
    };
  }, [modal, doc, busy]);
  // 입력이 700ms 동안 멈추면 저장한다. 오래된 응답이 최신 입력을 덮어쓰지 않게 한다.
  useEffect(() => {
    if (!state || state.verdict || notes === state.notes || busy) return;
    setNoteStatus('저장 대기 중');
    const timer = setTimeout(() => {
      const snapshot = notes;
      setNoteStatus('저장 중…');
      requestGame('notes', { text: snapshot })
        .then((savedState) => {
          if (!savedState) throw new Error('수사 기록이 없습니다.');
          if (latestNotes.current === snapshot) {
            setState(savedState);
            setNoteStatus('저장됨');
          }
        })
        .catch(() => setNoteStatus('저장 실패 · 다시 저장을 눌러주세요'));
    }, 700);
    return () => clearTimeout(timer);
  }, [notes, state?.notes, state?.id, state?.verdict, busy]);
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (stateRef.current && latestNotes.current !== stateRef.current.notes) {
        e.preventDefault();
        e.returnValue = '';
      }
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, []);
  // 사용자 동작에 따른 요청은 로딩/오류 상태를 공통으로 처리한다.
  /** 버튼에서 실행하는 요청의 로딩·오류·최신 수사 상태를 공통 처리한다. */
  async function updateGame(action: string, body: unknown) {
    if (actionLock.current) return null;
    actionLock.current = true;
    setBusy(true);
    setError('');
    try {
      const updatedState = await requestGame(action, body);
      setState(updatedState);
      return updatedState;
    } catch (e) {
      setState(currentGame());
      setError(e instanceof Error ? e.message : '요청에 실패했습니다.');
      return null;
    } finally {
      actionLock.current = false;
      setBusy(false);
    }
  }
  function navigateTo(v: View) {
    setView(v);
    setMobile(false);
    setError('');
    setDoc(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  async function startInvestigation(restart = false) {
    bgm.startFromGame(); // 클릭 처리 안에서 바로 호출해야 브라우저가 재생을 허용한다
    const updatedState = await updateGame('start', { restart });
    if (updatedState) {
      setNotes(updatedState.notes);
      setDoc(null);
      if (restart) {
        setNotes('');
        setForm({ suspectId: '', motive: '', method: '', evidenceIds: [] });
        setQuestion('');
        setTopicId('');
        setAttachment('');
      }
      setModal(null);
      navigateTo(updatedState.verdict ? 'results' : 'briefing');
    }
  }
  /** 열람 확정 후 서버에서 본문을 받아 원본 문서 팝업에 표시합니다. */
  async function openEvidence(id: string) {
    if (!state || actionLock.current) return;
    let readable = state;
    if (
      !state.examined.includes(id) &&
      !state.derivedEvidence[id] &&
      !state.statements[id]
    ) {
      const updated = await updateGame('examine', { evidenceId: id });
      if (!updated) return;
      readable = updated;
    }
    try {
      const document = await requestDocument(id, readable);
      setSelectedDoc(document);
      setDoc(id);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : '자료를 불러오지 못했습니다.',
      );
    }
  }
  /** 화면 입력만 전달한다. 남은 횟수와 증거 유효성의 최종 검사는 서버가 한다. */
  async function submitQuestion(e: React.FormEvent) {
    e.preventDefault();
    const updatedState = await updateGame('interrogate', {
      suspectId: suspect,
      question,
      topicId: topicId || undefined,
      evidenceId: attachment || undefined,
    });
    if (updatedState) {
      setQuestion('');
      setTopicId('');
      setAttachment('');
    }
  }
  const currentSuspect = suspects.find((person) => person.id === suspect)!;
  const inProgress = state && !state.verdict;

  return {
    view,
    setView,
    state,
    setState,
    ready,
    busy,
    error,
    setError,
    modal,
    setModal,
    doc,
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
  };
}

export type CaseGameController = ReturnType<typeof useCaseGame>;
