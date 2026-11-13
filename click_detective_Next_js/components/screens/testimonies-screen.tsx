'use client';
import { useState } from 'react';
import {useScreenView,type TestimonyView} from '@/hooks/use-screen-view';
import { ArrowUpRight, Check, MessageSquare, Search } from 'lucide-react';
import { suspects, evidence, type GameState } from '@/lib/case';
import type { CaseGameController } from '@/hooks/use-case-game';

type Props = Pick<CaseGameController, 'busy' | 'openEvidence' | 'navigateTo'> & {
  state: GameState;
};
export function TestimoniesScreen({ state, busy, openEvidence, navigateTo }: Props) {
  const witnesses = [{ id: 'butler', name: '집사 노씨' }, ...suspects];
  const [person, setPerson] = useState('all');
  const [search, setSearch] = useState('');
  const [section, setSection] = useState('all');
  const {visible,error} = useScreenView<TestimonyView>('testimonies',state,{search,person},{visible:[]});
  return (
    <>
      {error && <div className="error-toast" role="alert">{error}</div>}
      <div className="desk-heading">
        <div className="eyebrow">WITNESS STATEMENTS</div>
        <h1>
          증언 기록<span>.</span>
        </h1>
        <p>
          인물별 최초 진술과 실제 심문 기록을 확인하세요. 증언은 물증이나 검시 결과와
          구분해 판단해야 합니다.
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
        <section key={w.id} className="archive-section" aria-label={w.name}>
          <h2>
            <MessageSquare size={18} /> {w.name}
          </h2>
          {(section === 'all' ? w.records : []).map((item) => (
            <button
              key={item.id}
              className="evidence-card testimony-record"
              disabled={busy || (!!state.verdict && !state.examined.includes(item.id))}
              onClick={() => openEvidence(item.id)}
            >
              <div className="evidence-card-top">
                <span>{item.code} · 증언</span>
                {state.examined.includes(item.id) && (
                  <span className="read-label">
                    <Check size={12} />
                    열람 완료
                  </span>
                )}
              </div>
              <h3>{item.title}</h3>
              <p>{item.summary}</p>
              <span className="text-button">
                증언 열람 <ArrowUpRight size={14} />
              </span>
            </button>
          ))}
          {section === 'all' && w.initial && (
            <article className="panel testimony-entry">
              <span className="eyebrow">최초 진술</span>
              <p>{w.initial}</p>
            </article>
          )}
          {w.acquired
            .filter(
              (item) =>
                section === 'all' ||
                (section === 'relations'
                  ? item.topic.startsWith('about-')
                  : section === 'admission'
                    ? item.nature === '심문에서 인정'
                    : section === 'movement'
                      ? item.topic === 'movement' && item.nature !== '심문에서 인정'
                      : false),
            )
            .map((item) => (
              <article
                className="panel testimony-entry"
                key={item.id}
                id={'statement-' + item.id}
              >
                <span className="eyebrow">
                  {item.code} · {item.nature} {item.time && ' · ' + item.time}
                </span>
                <h3>{item.title}</h3>
                <p>{item.excerpt}</p>
                {Object.values(state.statements).some((next) =>
                  next.supersedes?.includes(item.id),
                ) && (
                  <p className="subtle">
                    이 주장과 다른 이후 인정이 확보되었습니다. 이전 발언은 원문대로
                    보존합니다.
                  </p>
                )}
                {item.supersedes?.some((id) => !!state.statements[id]) && (
                  <p className="subtle">기존 체류 주장에 대한 수정 진술입니다.</p>
                )}
                <div className="source-links">
                  <button onClick={() => openEvidence(item.id)}>
                    심문 원문 <ArrowUpRight size={12} />
                  </button>
                  {item.time && (
                    <button
                      onClick={() => {
                        navigateTo('timeline');
                        setTimeout(
                          () =>
                            document
                              .getElementById('timeline-statement-' + item.id)
                              ?.scrollIntoView({ behavior: 'smooth', block: 'center' }),
                          0,
                        );
                      }}
                    >
                      타임라인 <ArrowUpRight size={12} />
                    </button>
                  )}
                  {item.sourceRefs.map((ref) => (
                    <button key={ref.kind + ref.id} onClick={() => openEvidence(ref.id)}>
                      제시 자료 {ref.id} <ArrowUpRight size={12} />
                    </button>
                  ))}
                </div>
                <details>
                  <summary>대본 출처</summary>
                  <p>
                    {item.source.file} · {item.source.pages.join(', ')}쪽 ·{' '}
                    {item.source.section}
                  </p>
                </details>
              </article>
            ))}
          {(section === 'all' || section === 'transcript' ? w.pairs : []).map(
            ({ question, answer }) => (
              <article className="panel testimony-entry" key={question.index}>
                <span className="eyebrow">심문 기록</span>
                <p>
                  <strong>수사관</strong> · {question.text}
                </p>
                {question.evidenceId && (
                  <button
                    className="text-button"
                    onClick={() => openEvidence(question.evidenceId!)}
                  >
                    제시 자료:{' '}
                    {state.derivedEvidence[question.evidenceId]?.code ??
                      question.evidenceId}{' '}
                    ·{' '}
                    {state.derivedEvidence[question.evidenceId]?.title ??
                      evidence.find((item) => item.id === question.evidenceId)
                        ?.title}{' '}
                    <ArrowUpRight size={13} />
                  </button>
                )}
                {answer && (
                  <blockquote>
                    <strong>{w.name}</strong> · {answer.text}
                  </blockquote>
                )}
              </article>
            ),
          )}
        </section>
      ))}
      {section !== 'all' &&
        section !== 'transcript' &&
        !visible.some((w) =>
          w.acquired.some((item) =>
            section === 'relations'
              ? item.topic.startsWith('about-')
              : section === 'admission'
                ? item.nature === '심문에서 인정'
                : item.topic === 'movement' && item.nature !== '심문에서 인정',
          ),
        ) && <div className="empty">이 분류에서 확보한 진술이 없습니다.</div>}
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
