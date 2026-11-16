import { useEffect, type RefObject } from 'react';
import type { InvestigationDocument } from '../materials/document-types';

/** 새 대화가 생기면 마지막 메시지로 이동한다.
 * @param scrollEnd 마지막 말풍선 위치를 가리키는 참조.
 * @param count 현재 대화 개수.
 * @returns 없음. 대화 스크롤 효과를 등록한다.
 */
export function useMessageScroll(
  scrollEnd: RefObject<HTMLDivElement | null>,
  count: number | undefined,
) {
  useEffect(() => {
    scrollEnd.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [count]);
}

/** 팝업이 열린 동안 스크롤과 키보드 초점을 관리한다.
 * @param modal 열린 안내 팝업 이름.
 * @param doc 열린 문서 ID.
 * @param busy 요청 처리 중인지 여부.
 * @param setModal 안내 팝업을 열거나 닫는 함수.
 * @param setDoc 문서 팝업을 열거나 닫는 함수.
 * @param setSelectedDoc 표시할 문서 본문을 바꾸는 함수.
 * @returns 없음. 팝업 키보드·스크롤 효과를 등록한다.
 */
export function useDialogEffects(
  modal: string | null,
  doc: string | null,
  busy: boolean,
  setModal: (modal: string | null) => void,
  setDoc: (doc: string | null) => void,
  setSelectedDoc: (doc: InvestigationDocument | undefined) => void,
) {
  useEffect(() => {
    if (!doc) setSelectedDoc(undefined);
    if (!modal && !doc) return;
    const previous = document.activeElement as HTMLElement | null;
    const old = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    /** 현재 화면의 키보드 또는 탭 종료 이벤트를 처리한다.
     * @param e 사용자 입력 또는 키보드 이벤트.
     * @returns 없음. 브라우저 이벤트와 화면 상태를 처리한다.
     */
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
}
