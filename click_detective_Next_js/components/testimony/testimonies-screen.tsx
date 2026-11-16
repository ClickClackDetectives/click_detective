'use client';
import { useState } from 'react';
import { WitnessSection } from './witness-section';
import { matchesSection } from '../../app/game/testimony/sections';
import { useScreenView, type TestimonyView } from '@/app/game/materials/use-screen-view';
import { ArrowUpRight, Search } from 'lucide-react';
import { suspects } from '@/app/game/catalog/catalog';
import type { GameState } from '@/app/game/investigation/types';
import type { CaseGameController } from '@/app/game/investigation/use-case-game';

type Props = Pick<CaseGameController, 'busy' | 'openEvidence' | 'navigateTo'> & {
  state: GameState;
};
/** 인물과 분류에 맞는 진술·심문 기록을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.busy 요청 처리 중인지 여부.
 * @param props.openEvidence 자료를 열람하고 문서 팝업을 여는 함수.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function TestimoniesScreen({ state, busy, openEvidence, navigateTo }: Props) {
  const witnesses = [{ id: 'butler', name: '집사 노씨' }, ...suspects];
  const [person, setPerson] = useState('all');
  const [search, setSearch] = useState('');
  const [section, setSection] = useState('all');
  const { visible, error } = useScreenView<TestimonyView>(
    'testimonies',
    state,
    { search, person },
    { visible: [] },
  );
  return (
    <>
      {error && (
        <div className="error-toast" role="alert">
          {error}
        </div>
      )}
      <div className="desk-heading">
        <div className="eyebrow">WITNESS STATEMENTS</div>
        <h1>
          증언 기록<span>.</span>
        </h1>
        <p>
          인물별 최초 진술과 실제 심문 기록을 확인하세요. 증언은 물증이나 검시 결과와 구분해
          판단해야 합니다.
        </p>
      </div>
      <div className="archive-groups" role="group" aria-label="증언자 선택">
        {[{ id: 'all', name: '전체' }, ...witnesses].map((w) => (
          <button
            key={w.id}
            aria-pressed={person === w.id}
            className={person === w.id ? 'selected' : ''}
            onClick={() => setPerson(w.id)}
          >
            {w.name}
          </button>
        ))}
      </div>
      <div className="archive-groups" role="group" aria-label="증언 분류">
        {[
          ['all', '전체'],
          ['movement', '확보한 동선 진술'],
          ['relations', '다른 인물에 대한 진술'],
          ['admission', '심문에서 인정'],
          ['transcript', '전체 심문 대화'],
        ].map(([id, label]) => (
          <button
            key={id}
            aria-pressed={section === id}
            className={section === id ? 'selected' : ''}
            onClick={() => setSection(id)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="toolbar">
        <span>최초 진술 · 집사 증언 · 심문 대화</span>
        <label className="search">
          <Search size={16} />
          <input
            aria-label="증언 검색"
            placeholder="인물·내용·증거 번호 검색"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
      </div>
      {visible.map((w) => (
        <WitnessSection
          key={w.id}
          w={w}
          state={state}
          section={section}
          busy={busy}
          openEvidence={openEvidence}
          navigateTo={navigateTo}
        />
      ))}
      {section !== 'all' &&
        section !== 'transcript' &&
        !visible.some((w) => w.acquired.some((item) => matchesSection(item, section))) && (
          <div className="empty">이 분류에서 확보한 진술이 없습니다.</div>
        )}
      {!visible.length && <div className="empty">검색 결과가 없습니다.</div>}
      {!state.messages.length && (
        <div className="panel empty">
          <p>심문을 진행하면 질문과 답변이 인물별 기록에 추가됩니다.</p>
          <button className="text-button" onClick={() => navigateTo('interrogate')}>
            용의자 심문으로 이동 <ArrowUpRight size={14} />
          </button>
        </div>
      )}
    </>
  );
}
