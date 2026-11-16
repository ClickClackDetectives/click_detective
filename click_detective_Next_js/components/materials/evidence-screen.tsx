'use client';
import { useState } from 'react';
import { useScreenView, type EvidenceView } from '@/app/game/materials/use-screen-view';
import { getSecondRoundEligibility, secondRoundRequirements } from '@/app/game/investigation/stage';
import { ArrowUpRight, Check, FileText, Search } from 'lucide-react';
import type { GameState } from '@/app/game/investigation/types';
import type { CaseGameController } from '@/app/game/investigation/use-case-game';
type Props = Omit<
  Pick<
    CaseGameController,
    'state' | 'filter' | 'setFilter' | 'busy' | 'openEvidence' | 'updateGame'
  >,
  'state'
> & { state: GameState };
/** 장소와 검색 조건에 맞는 증거 목록을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.filter 자료 검색창의 입력값.
 * @param props.setFilter 자료 검색 입력값을 바꾸는 함수.
 * @param props.busy 요청 처리 중인지 여부.
 * @param props.openEvidence 자료를 열람하고 문서 팝업을 여는 함수.
 * @param props.updateGame 행동 이름과 입력을 서버에 보내고 최신 상태를 적용하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function EvidenceScreen({
  state,
  filter,
  setFilter,
  busy,
  openEvidence,
  updateGame,
}: Props) {
  const [place, setPlace] = useState('all');
  const { available, groups, places, readCount, error } = useScreenView<EvidenceView>(
    'evidence',
    state,
    { search: filter, place },
    { available: [], groups: [], places: [], readCount: 0 },
  );
  const eligibility = getSecondRoundEligibility(state);
  return (
    <>
      {error && (
        <div className="error-toast" role="alert">
          {error}
        </div>
      )}
      <div className="desk-heading">
        <div className="eyebrow">EVIDENCE ROOM · PHASE {state.phase}</div>
        <h1>
          증거 보관실<span>.</span>
        </h1>
        <p>
          장소를 선택해 물증과 문서를 조사하세요. 인물의 말은 증언 기록에서 확인할 수 있습니다.
          소지품은 발견 장소와 구분해 표시합니다.
        </p>
      </div>
      {state.phase === 1 && !state.verdict && (
        <div className="phase-notice">
          <div>
            <strong>닫힌 기록을 열 단서</strong>
            <p>
              추론 증거 {eligibility.inference}/{secondRoundRequirements.inference}개 · 심문 쟁점{' '}
              {eligibility.findings}/{secondRoundRequirements.findings}개. 각각 2개 이상 확보하면
              검시 소견과 추가 단서가 공개됩니다.
            </p>
          </div>
          <button
            className="primary small"
            disabled={busy || !eligibility.eligible}
            onClick={() => updateGame('advance', {})}
          >
            2차 조사 시작 <ArrowUpRight size={16} />
          </button>
        </div>
      )}
      {state.phase === 2 && (
        <div className="phase-notice">
          <div>
            <strong>2차 조사 · 드러나는 비밀</strong>
            <p>검시 소견이 도착했습니다. 새 증거와 앞선 진술을 비교하세요.</p>
          </div>
        </div>
      )}
      <div className="archive-groups" role="group" aria-label="증거 장소 선택">
        {['all', ...places].map((name) => (
          <button
            key={name}
            aria-pressed={place === name}
            className={place === name ? 'selected' : ''}
            onClick={() => setPlace(name)}
          >
            {name === 'all' ? '전체' : name}
            <small>{available.filter((item) => name === 'all' || item.type === name).length}</small>
          </button>
        ))}
      </div>
      <div className="toolbar">
        <span>
          {available.length}개 자료 <i /> {readCount}개 열람
        </span>
        <label className="search">
          <Search size={16} />
          <input
            placeholder="증거 검색"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            aria-label="증거 검색"
          />
        </label>
      </div>
      {groups.map((group) => (
        <section key={group.name} className="archive-section" aria-label={group.name}>
          <h2>
            {group.name} <small>{group.records.length}개 자료</small>
          </h2>
          <div className="evidence-grid">
            {group.records.map((e) => (
              <button
                disabled={busy || (!!state.verdict && !state.examined.includes(e.id))}
                key={e.id}
                className="evidence-card"
                onClick={() => openEvidence(e.id)}
              >
                <div className="evidence-card-top">
                  <span>{e.code}</span>
                  {state.examined.includes(e.id) ? (
                    <span className="read-label">
                      <Check size={12} />
                      열람 완료
                    </span>
                  ) : (
                    <span className="unread-dot" />
                  )}
                </div>
                <div className="document-symbol">
                  <FileText size={29} />
                  <span>{e.type}</span>
                </div>
                <h3>{e.title}</h3>
                <p>{e.summary}</p>
                <div className="evidence-card-bottom">
                  <span>
                    {e.time} · {e.type}
                  </span>
                  <ArrowUpRight size={16} />
                </div>
              </button>
            ))}
          </div>
        </section>
      ))}
      {!groups.length && <div className="empty">현재 조사 단계에서 검색 결과가 없습니다.</div>}
    </>
  );
}
