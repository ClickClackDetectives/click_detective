import { ArrowRight, Check, X } from 'lucide-react';

import { evidenceIllustrations } from '@/app/game/materials/illustrations';

import type { CaseGameController } from '@/app/game/investigation/use-case-game';

type Props = Pick<CaseGameController, 'selectedDoc' | 'setDoc' | 'setAttachment' | 'navigateTo'>;

/** 확보한 문서 본문과 이미지, 자료 제시 버튼을 팝업으로 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.selectedDoc 팝업에 표시할 문서 본문과 메타데이터.
 * @param props.setDoc 문서 팝업을 열거나 닫는 함수.
 * @param props.setAttachment 심문에 첨부할 자료를 바꾸는 함수.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function EvidenceDialog({ selectedDoc, setDoc, setAttachment, navigateTo }: Props) {
  if (!selectedDoc) return null;
  return (
    <div className="modal-backdrop" onClick={() => setDoc(null)}>
      <section
        className="modal document-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="doc-title"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          autoFocus
          className="close-modal"
          aria-label="증거 닫기"
          onClick={() => setDoc(null)}
        >
          <X size={20} />
        </button>
        <div className="eyebrow">
          {selectedDoc.code} · {selectedDoc.type}
        </div>
        <h2 id="doc-title">{selectedDoc.title}</h2>
        <div className="document-body">{selectedDoc.body}</div>
        {evidenceIllustrations[selectedDoc.id] && (
          <figure className="evidence-illustration">
            <img
              src={evidenceIllustrations[selectedDoc.id]}
              alt={`${selectedDoc.title} — 증거 참고 일러스트`}
              width={1200}
              height={900}
            />
            <figcaption>
              증거 참고 일러스트 · 정확한 단서와 수치는 위 설명을 기준으로 확인하세요.
            </figcaption>
          </figure>
        )}
        <div className="modal-bottom">
          <span>
            <Check size={14} /> 기록 열람 완료
          </span>
          {'kind' in selectedDoc && selectedDoc.kind === 'testimony' ? (
            <span>확보한 증언 원문 · 읽기 전용</span>
          ) : (
            <button
              className="primary small"
              onClick={() => {
                setAttachment(selectedDoc.id);
                setDoc(null);
                navigateTo('interrogate');
              }}
            >
              심문에 증거 제시 <ArrowRight size={15} />
            </button>
          )}
        </div>
      </section>
    </div>
  );
}
