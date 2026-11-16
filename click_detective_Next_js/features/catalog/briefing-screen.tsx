import { CaseOpening } from '@/features/catalog/case-opening';
import { ArrowRight, AudioLines, Fingerprint, Shield } from 'lucide-react';
import { evidence, suspects, questionLimit } from '@/features/catalog/catalog';
import type { GameState } from '@/features/investigation/types';
import type { CaseGameController } from '@/features/investigation/use-case-game';

type Props = Omit<Pick<CaseGameController, 'state' | 'navigateTo'>, 'state'> & {
  state: GameState;
};

/** 사건 개요와 오프닝 재생 버튼을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function BriefingScreen({ state, navigateTo }: Props) {
  return (
    <>
      <div className="desk-heading">
        <div className="eyebrow">CASE BRIEFING · #0001</div>
        <h1>열세 번째 종</h1>
        <p>모두가 무언가를 숨기고 있습니다. 사실부터 확인하세요.</p>
      </div>
      <CaseOpening gameId={state.id} />
      <div className="brief-grid">
        <article className="paper">
          <div className="paper-top">
            <Shield size={26} />
            <span>
              BLACK CLOUD MANOR
              <br />
              사건 개요 보고서
            </span>
            <span className="confidential">CONFIDENTIAL</span>
          </div>
          <p className="mono">사건 #0001 · 흑운장 · 폭풍우의 밤</p>
          <h2>
            열세 번째 종이 울리고,
            <br />한 사람은 돌아가지 못했다.
          </h2>
          <p>
            일흔 번째 생일 만찬에서 백도현 회장은 자정에 유언장을 바꾸겠다고 선언했습니다. 밤 11시
            30분, 집사가 서재에서 회장의 시신을 발견했습니다.
          </p>
          <p>
            뒤통수에는 둔기에 맞은 상처가 남아 있고, 와인잔 바닥에는 흰 가루가 보입니다. 폭풍우로
            다리는 끊겼고 전화는 닿지 않습니다. 다섯 용의자의 진술과 증거를 대조하세요.
          </p>
          <div className="paper-note">
            당신의 임무
            <br />
            <strong>
              증거를 연결하고, 거짓 진술을 밝혀내고,
              <br />
              범인과 동기, 범행 수단을 입증하세요.
            </strong>
          </div>
          <div className="paper-sign">
            배정 수사관: YOU <Fingerprint size={38} />
          </div>
        </article>
        <div className="brief-side">
          <div className="panel">
            <div className="panel-label">INVESTIGATION OVERVIEW</div>
            <div className="stat-line">
              <span>확보한 증거</span>
              <strong>
                {evidence.filter((e) => e.phase <= state.phase).length} <small>FILES</small>
              </strong>
            </div>
            <div className="stat-line">
              <span>핵심 용의자</span>
              <strong>
                {suspects.length} <small>PERSONS</small>
              </strong>
            </div>
            <div className="stat-line">
              <span>전체 심문 가능 횟수</span>
              <strong>
                {questionLimit - state.questions} <small>LEFT</small>
              </strong>
            </div>
          </div>
          <div className="panel next-step">
            <span className="eyebrow">RECOMMENDED NEXT STEP</span>
            <h3>기록은 거짓말하지 않습니다.</h3>
            <p>
              추론 증거 2개 이상과 심문 쟁점 2개 이상을 확보하면 증거실에서 2차 조사를 열 수
              있습니다. 증거는 한 번에 하나씩 첨부하되 같은 인물에게 제시한 기록을 함께 대조합니다.
            </p>
            <button className="primary full" onClick={() => navigateTo('evidence')}>
              증거 살펴보기 <ArrowRight size={16} />
            </button>
          </div>
          <div className="demo-note">
            <AudioLines size={16} />
            <p>
              심문 대사는 FastAPI의 LLM 생성·검증 과정을 거쳐 전달됩니다. 연결된 백엔드의 실행
              모드에 따라 실제 모델 또는 테스트 응답을 사용합니다.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
