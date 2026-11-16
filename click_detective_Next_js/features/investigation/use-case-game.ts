'use client';
import { useRef, useState } from 'react';
import { useRestoreGame } from './use-restore-game';
import { useMessageScroll, useDialogEffects } from './use-dialog-effects';
import { useNotesAutosave } from '../notes/use-notes-autosave';
import { suspects } from '@/features/catalog/catalog';
import type { GameState, SuspectId } from '@/features/investigation/types';
import type { InvestigationDocument } from '@/features/materials/document-types';
import { requestGame, requestDocument, currentGame } from '@/features/investigation/game-client';
import type { View } from '@/features/application/navigation';

/** 화면 상태와 서버 요청을 연결한다. 화면 마크업은 각 features 폴더에 있다.
 * 파라미터 없음.
 * @returns 수사 상태, 화면 입력값과 행동 함수 묶음.
 */
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
  const active = state !== null && view !== 'home' && view !== 'cases';
  useRestoreGame(setState, setNotes, setError, setReady);
  useMessageScroll(scrollEnd, state?.messages.length);
  useDialogEffects(modal, doc, busy, setModal, setDoc, setSelectedDoc);
  useNotesAutosave({ state, notes, busy, setState, setNoteStatus });
  // 사용자 동작에 따른 요청은 로딩/오류 상태를 공통으로 처리한다.
  /** 버튼에서 실행하는 요청의 로딩·오류·최신 수사 상태를 공통 처리한다.
   * @param action 실행할 수사 행동 이름.
   * @param body 전송할 요청 본문.
   * @returns 성공하면 최신 수사 상태, 실패하거나 잠겨 있으면 null.
   */
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
  /** 선택한 화면으로 이동하고 팝업·모바일 메뉴를 정리한다.
   * @param v 이동할 화면.
   * @returns 없음. 화면 상태를 바꾼다.
   */
  function navigateTo(v: View) {
    setView(v);
    setMobile(false);
    setError('');
    setDoc(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
  /** 기존 수사를 이어가거나 새로운 수사를 만든다.
   * @param restart 현재 기록을 초기화하고 새 수사를 만들지 여부.
   * @returns 수사 생성·복원과 화면 이동이 끝나면 완료되는 Promise.
   */
  async function startInvestigation(restart = false) {
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
  /** 열람 확정 후 서버에서 본문을 받아 원본 문서 팝업에 표시합니다.
   * @param id 자료 또는 수사 식별자.
   * @returns 문서 조회·표시를 마치면 완료되는 Promise.
   */
  async function openEvidence(id: string) {
    if (!state || actionLock.current) return;
    let readable = state;
    if (!state.examined.includes(id) && !state.derivedEvidence[id] && !state.statements[id]) {
      const updated = await updateGame('examine', { evidenceId: id });
      if (!updated) return;
      readable = updated;
    }
    try {
      const document = await requestDocument(id, readable);
      setSelectedDoc(document);
      setDoc(id);
    } catch (error) {
      setError(error instanceof Error ? error.message : '자료를 불러오지 못했습니다.');
    }
  }
  /** 화면 입력만 전달한다. 남은 횟수와 증거 유효성의 최종 검사는 서버가 한다.
   * @param e 사용자 입력 또는 키보드 이벤트.
   * @returns 심문과 입력 초기화를 마치면 완료되는 Promise.
   */
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
