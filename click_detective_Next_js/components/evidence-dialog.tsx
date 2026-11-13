import { ArrowRight, Check, X } from 'lucide-react';

import { evidenceIllustrations } from '@/lib/evidence-illustrations';

import type { CaseGameController } from '@/hooks/use-case-game';

type Props = Pick<
  CaseGameController,
  'selectedDoc' | 'setDoc' | 'setAttachment' | 'navigateTo'
>;

export function EvidenceDialog({
  selectedDoc,
  setDoc,
  setAttachment,
  navigateTo,
}: Props) {
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
