'use client';
import {
  describeSource,
  getInferenceBasisLabel,
  getInferenceSources,
  sourceLabels,
  type SourceCategory,
} from '@/lib/inference-sources';
import { useState } from 'react';
import {useScreenView,type InferenceView} from '@/hooks/use-screen-view';
import { ArrowRight, Link2, FileText, MessageSquare, Search } from 'lucide-react';
import { type GameState, type SourceRef } from '@/lib/case';
import type { CaseGameController } from '@/hooks/use-case-game';
type Props = Omit<
  Pick<
    CaseGameController,
    'state' | 'busy' | 'updateGame' | 'openEvidence' | 'navigateTo'
  >,
  'state'
> & { state: GameState };
function key(ref: SourceRef) {
  return ref.kind + ':' + ref.id;
}
export function InferenceScreen({
  state,
  busy,
  updateGame,
  openEvidence,
  navigateTo,
}: Props) {
  const [selected, setSelected] = useState<SourceRef[]>([]);
  const [notice, setNotice] = useState('');
  const [category, setCategory] = useState<SourceCategory>('evidence');
  const [search, setSearch] = useState('');
  const sources = getInferenceSources(state);
  const derived = Object.values(state.derivedEvidence);
  const {visible,error} = useScreenView<InferenceView>('inference',state,{search,category},{visible:[]});
  function title(ref: SourceRef) {
    const item = describeSource(state, ref);
    return `${sourceLabels[item.category]} ${item.code} · ${item.title}`;
  }
  function open(ref: SourceRef) {
    void openEvidence(ref.id);
  }
  function toggle(ref: SourceRef) {
    setNotice('');
    setSelected((previous) =>
      previous.some((item) => key(item) === key(ref))
        ? previous.filter((item) => key(item) !== key(ref))
        : previous.length < 4
          ? [...previous, ref]
          : previous,
    );
  }
  async function connect() {
    setNotice('');
    const before = derived.length;
    const updated = await updateGame('connect-evidence', { sources: selected });
    if (updated) {
      setSelected([]);
      setNotice(
        Object.keys(updated.derivedEvidence).length > before
          ? '새 추론 증거를 확보했습니다.'
          : '이미 확보한 연결입니다. 같은 추론 증거를 중복 생성하지 않았습니다.',
      );
    }
  }
  return (
    <>
      {error && <div className="error-toast" role="alert">{error}</div>}
      <div className="desk-heading">
        <div className="eyebrow">EVIDENCE CONNECTIONS</div>
        <h1>
          추론 증거<span>.</span>
        </h1>
        <p>
          열람한 증거·증언을 연결해 새로운 추론 증거를 확보하세요. 원본 자료와 수사관의
          추론은 구분해 기록합니다.
        </p>
      </div>
      <section className="panel connection-builder">
        <h3>
          <Link2 size={18} /> 자료 연결
        </h3>
        <p>
          연관된 자료 2~4개를 선택하세요. 같은 결론을 여러 근거 조합으로 도출할 수
          있습니다. 추론 증거를 다른 자료와 다시 연결할 수도 있습니다.
        </p>
        <div className="archive-groups" role="group" aria-label="연결 자료 종류">
          {(Object.keys(sourceLabels) as SourceCategory[]).map((kind) => (
            <button
              key={kind}
              aria-pressed={category === kind}
              className={category === kind ? 'selected' : ''}
              onClick={() => setCategory(kind)}
            >
              {sourceLabels[kind]}{' '}
              <small>{sources.filter((item) => item.category === kind).length}개</small>
            </button>
          ))}
        </div>
        <label className="search inference-search">
          <Search size={16} />
          <input
            aria-label="연결 자료 검색"
            placeholder="번호·제목·인물 검색"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <div className="connection-options">
          {visible.map((item) => (
            <label key={key(item.ref)}>
              <input
                type="checkbox"
                disabled={
                  busy ||
                  !!state.verdict ||
                  (selected.length >= 4 &&
                    !selected.some((ref) => key(ref) === key(item.ref)))
                }
                checked={selected.some((ref) => key(ref) === key(item.ref))}
                onChange={() => toggle(item.ref)}
              />
              {item.category === 'derived' ? (
                <Link2 size={16} />
              ) : item.category === 'testimony' ? (
                <MessageSquare size={16} />
              ) : (
                <FileText size={16} />
              )}
              <span className="connection-source">
                <strong>
                  {item.code} · {item.title}
                </strong>
                <small>{item.context}</small>
              </span>
            </label>
          ))}
        </div>
        {!visible.length && (
          <div className="empty">
            {search
              ? '검색 결과가 없습니다.'
              : `아직 확보한 ${sourceLabels[category]} 자료가 없습니다.`}
            <br />
            <button
              className="text-button"
              onClick={() =>
                navigateTo(
                  category === 'testimony'
                    ? 'testimonies'
                    : category === 'derived'
                      ? 'evidence'
                      : 'evidence',
                )
              }
            >
              자료 확보하기 <ArrowRight size={14} />
            </button>
          </div>
        )}
        <div className="selected-sources" aria-label="선택한 연결 자료">
          <strong>선택한 자료 {selected.length}/4</strong>
          {selected.length === 0 ? (
            <p>분류를 오가며 증거·증언·추론을 함께 선택할 수 있습니다.</p>
          ) : (
            selected.map((ref) => (
              <button
                key={key(ref)}
                disabled={busy || !!state.verdict}
                onClick={() => toggle(ref)}
                aria-label={title(ref) + ' 선택 해제'}
              >
                {title(ref)} ×
              </button>
            ))
          )}
        </div>
        <div className="connection-actions">
          <span>{selected.length}/4 선택</span>
          <button
            className="primary small"
            disabled={busy || !!state.verdict || selected.length < 2}
            onClick={connect}
          >
            <Link2 size={14} />
            선택한 자료 연결
          </button>
        </div>
        <p role="status" className="connection-notice">
          {state.verdict ? '종결된 사건의 연결 기록은 읽기 전용입니다.' : notice}
        </p>
      </section>
      <section className="findings-section">
        <h2>
          추론 증거 <small aria-live="polite">{derived.length}개</small>
        </h2>
        {derived.length === 0 ? (
          <p className="empty">아직 생성한 추론 증거가 없습니다.</p>
        ) : (
          <div className="derived-grid">
            {derived.map((item) => (
              <article className="panel" key={item.id}>
                <span className="eyebrow">{item.code} · 추론 증거</span>
                <span className="inference-kind">
                  {item.investigationPhase === 1 ? '1차 전용' : '2차 조사'} ·{' '}
                  {item.construction === 'chain' ? '연쇄 추론' : '기본 추론'}
                </span>
                <h3>{item.title}</h3>
                <span className="inference-kind">
                  {getInferenceBasisLabel(state, item.leafSources)}
                </span>
                <h4>도출한 결론</h4>
                <p>{item.body}</p>
                <h4>직접 연결한 자료</h4>
                <div className="source-links">
                  {item.sourceRefs.map((ref) => (
                    <button key={key(ref)} onClick={() => open(ref)}>
                      {title(ref)} <ArrowRight size={12} />
                    </button>
                  ))}
                </div>
                <details className="inference-origins">
                  <summary>원본 근거 {item.leafSources.length}개 확인</summary>
                  <div className="source-links">
                    {item.leafSources.map((ref) => (
                      <button key={key(ref)} onClick={() => open(ref)}>
                        {title(ref)} <ArrowRight size={12} />
                      </button>
                    ))}
                  </div>
                </details>
                <button className="text-button" onClick={() => openEvidence(item.id)}>
                  증거 열람·심문에 제시 <ArrowRight size={14} />
                </button>
              </article>
            ))}
          </div>
        )}
      </section>
    </>
  );
}
