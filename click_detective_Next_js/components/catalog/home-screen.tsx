import {
  ArrowRight,
  ArrowUpRight,
  Check,
  FileText,
  Fingerprint,
  FolderOpen,
  Gavel,
  MessageSquare,
  LoaderCircle,
} from 'lucide-react';

import type { CaseGameController } from '@/app/game/investigation/use-case-game';

type Props = Pick<
  CaseGameController,
  'busy' | 'ready' | 'inProgress' | 'startInvestigation' | 'navigateTo'
>;

/** 시작·이어하기 버튼이 있는 홈 화면을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.busy 요청 처리 중인지 여부.
 * @param props.ready 최초 수사 복원 요청이 끝났는지 여부.
 * @param props.inProgress 진행 중인 수사가 있으면 해당 상태, 없으면 null 또는 false.
 * @param props.startInvestigation 기존 수사를 이어가거나 새 수사를 만드는 함수.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function HomeScreen({ busy, ready, inProgress, startInvestigation, navigateTo }: Props) {
  return (
    <main>
      <section className="hero">
        <div className="hero-grain" />
        <div className="hero-content">
          <div className="eyebrow">
            <span /> BLACK CLOUD MANOR · CASE 001
          </div>
          <h1>
            모든 진술에는
            <br />
            <em>빈틈이 있다.</em>
          </h1>
          <p>
            다섯 명의 용의자. 모두가 비밀을 숨기는 밤.
            <br />
            질문하고, 의심하고, 당신의 언어로 진실을 밝혀내세요.
          </p>
          <div className="hero-actions">
            <button
              className="primary"
              disabled={busy || !ready}
              onClick={() => startInvestigation()}
            >
              {busy ? <LoaderCircle className="spin" size={17} /> : <FolderOpen size={18} />}{' '}
              {inProgress ? '수사 이어하기' : '첫 번째 사건 시작하기'}
              <ArrowRight size={18} />
            </button>
            <button className="text-button" onClick={() => navigateTo('cases')}>
              사건 목록 보기 <ArrowUpRight size={16} />
            </button>
          </div>
          <div className="hero-meta">
            <span>
              <Check size={13} /> 무료 플레이
            </span>
            <span>
              <Check size={13} /> 가입 없이 시작
            </span>
            <span>
              <Check size={13} /> 다운로드 불필요
            </span>
          </div>
        </div>
        <div className="hero-file">
          <span className="red-stamp">UNSOLVED</span>
          <div className="file-top">
            <span>CASE FILE</span>
            <span>01 / 01</span>
          </div>
          <div className="file-bottom">
            <div className="eyebrow">사건 번호 #0001</div>
            <h2>
              THE THIRTEENTH
              <br />
              BELL<span>.</span>
            </h2>
            <p>열세 번째 종</p>
            <div className="file-rule" />
            <span className="location">
              <i /> BLACK CLOUD MANOR · 23:30
            </span>
          </div>
        </div>
        <div className="hero-bottom">
          <span>THE TRUTH DOESN’T REVEAL ITSELF.</span>
          <span>SCROLL TO INVESTIGATE ↓</span>
        </div>
      </section>
      <section className="process">
        <div className="section-label">
          <span>HOW TO INVESTIGATE</span>
          <p>당신의 직감에, 증거를 더하세요.</p>
        </div>
        <div className="process-grid">
          {[
            {
              n: '01',
              icon: FileText,
              title: '기록을 읽으세요',
              text: '진술서, 출입 기록, 감식 보고서. 사소한 한 줄이 사건을 바꿉니다.',
            },
            {
              n: '02',
              icon: MessageSquare,
              title: '누구든 의심하세요',
              text: '정해진 선택지 없이 질문하세요. 증거를 내밀면 진술은 흔들립니다.',
            },
            {
              n: '03',
              icon: Fingerprint,
              title: '모순을 연결하세요',
              text: '시간과 진술 사이의 빈틈. 사실이 맞지 않는 지점을 찾아내세요.',
            },
            {
              n: '04',
              icon: Gavel,
              title: '범인을 지목하세요',
              text: '누가, 왜, 어떻게. 당신이 찾은 증거로 사건을 종결하세요.',
            },
          ].map((x) => (
            <article key={x.n}>
              <div className="process-number">
                {x.n}
                <x.icon size={20} />
              </div>
              <h3>{x.title}</h3>
              <p>{x.text}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="archive-teaser">
        <div>
          <div className="eyebrow">THE CASE ARCHIVE</div>
          <h2>
            다음 사건은,
            <br />
            당신을 기다립니다.
          </h2>
          <p>흑운장의 생일 만찬부터, 열세 번째 종이 울린 밤의 진실까지.</p>
        </div>
        <button className="outline" onClick={() => navigateTo('cases')}>
          사건 기록실 열기 <ArrowRight size={16} />
        </button>
      </section>
    </main>
  );
}
