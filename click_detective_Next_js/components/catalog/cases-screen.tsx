import { caseLibrary } from '@/app/game/catalog/case-library';
import { ArrowRight, Clock3, Fingerprint, LockKeyhole } from 'lucide-react';

import type { CaseGameController } from '@/app/game/investigation/use-case-game';

type Props = Pick<
  CaseGameController,
  'busy' | 'ready' | 'inProgress' | 'startInvestigation' | 'setModal'
>;

/** 사건 카드와 준비 중 사건 안내를 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.busy 요청 처리 중인지 여부.
 * @param props.ready 최초 수사 복원 요청이 끝났는지 여부.
 * @param props.inProgress 진행 중인 수사가 있으면 해당 상태, 없으면 null 또는 false.
 * @param props.startInvestigation 기존 수사를 이어가거나 새 수사를 만드는 함수.
 * @param props.setModal 안내 팝업을 열거나 닫는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function CasesScreen({ busy, ready, inProgress, startInvestigation, setModal }: Props) {
  return (
    <main className="library wrap">
      <div className="eyebrow">CLICK DETECTIVE CLUB ARCHIVE</div>
      <div className="page-heading">
        <div>
          <h1>
            사건 기록실<span>.</span>
          </h1>
          <p>진실은 기록 속에 있습니다. 수사를 시작할 사건을 선택하세요.</p>
        </div>
        <span className="counter">{String(caseLibrary.length).padStart(2, '0')} CASE FILES</span>
      </div>
      <div className="case-grid">
        {caseLibrary.map((c, i) => (
          <article className={'case-card case-' + i} key={c.id}>
            <div className="case-art">
              <span className="case-art-number">0{i + 1}</span>
              <span className={'badge ' + (i === 0 ? 'green' : '')}>
                {i === 0 ? '무료 사건' : '준비 중'}
              </span>
              <Fingerprint size={100} />
            </div>
            <div className="case-card-body">
              <div className="eyebrow">
                CASE #{c.id} <span>· {c.level}</span>
              </div>
              <h2>{c.title}</h2>
              <h3>{c.ko}</h3>
              <p>{c.desc}</p>
              <div className="case-facts">
                <span>
                  <Clock3 size={13} />
                  {c.duration}
                </span>
                <span>{c.place}</span>
              </div>
              <button
                disabled={busy || !ready}
                className={i === 0 ? 'primary full' : 'outline full'}
                onClick={() => (i === 0 ? startInvestigation() : setModal('pack'))}
              >
                {i === 0 ? (
                  inProgress ? (
                    '수사 이어하기'
                  ) : (
                    '사건 파일 열기'
                  )
                ) : (
                  <>
                    <LockKeyhole size={14} /> 후속 사건 안내
                  </>
                )}
                <ArrowRight size={16} />
              </button>
            </div>
          </article>
        ))}
      </div>
      <p className="library-note">
        첫 번째 사건은 완주 가능한 독립 데모입니다. 후속 사건과 유료 결제는 제공하지 않습니다.
      </p>
    </main>
  );
}
