'use client';
import {
  describeSource,
  getInferenceSources,
  sourceLabels,
  type SourceCategory,
} from '@/features/inference/sources';
import { DerivedList } from './derived-list';
import { sourceKey as key } from './sources';
import { useState } from 'react';
import { useScreenView, type InferenceView } from '@/features/materials/use-screen-view';
import { ArrowRight, Link2, FileText, MessageSquare, Search } from 'lucide-react';
import type { GameState, SourceRef } from '@/features/investigation/types';
import type { CaseGameController } from '@/features/investigation/use-case-game';
type Props = Omit<
  Pick<CaseGameController, 'state' | 'busy' | 'updateGame' | 'openEvidence' | 'navigateTo'>,
  'state'
> & { state: GameState };
/** 연결할 자료 선택과 확보한 추론을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.busy 요청 처리 중인지 여부.
 * @param props.updateGame 행동 이름과 입력을 서버에 보내고 최신 상태를 적용하는 함수.
 * @param props.openEvidence 자료를 열람하고 문서 팝업을 여는 함수.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function InferenceScreen({ state, busy, updateGame, openEvidence, navigateTo }: Props) {
  const [selected, setSelected] = useState<SourceRef[]>([]);
  const [notice, setNotice] = useState('');
  const [category, setCategory] = useState<SourceCategory>('evidence');
  const [search, setSearch] = useState('');
  const sources = getInferenceSources(state);
  const derived = Object.values(state.derivedEvidence);
  const { visible, error } = useScreenView<InferenceView>(
    'inference',
    state,
    { search, category },
    { visible: [] },
  );
  /** 출처의 화면용 제목을 만든다.
   * @param ref 자료 종류와 ID가 담긴 출처.
   * @returns 출처의 화면용 제목 문자열.
   */
  function title(ref: SourceRef) {
    const item = describeSource(state, ref);
    return `${sourceLabels[item.category]} ${item.code} · ${item.title}`;
  }
  /** 선택한 출처의 자료를 연다.
   * @param ref 자료 종류와 ID가 담긴 출처.
   * @returns 없음. 선택한 자료를 여는 비동기 작업을 시작한다.
   */
  function open(ref: SourceRef) {
    void openEvidence(ref.id);
  }
  /** 선택한 자료를 추가하거나 해제한다.
   * @param ref 자료 종류와 ID가 담긴 출처.
   * @returns 없음. 선택한 자료 목록을 바꾼다.
   */
  function toggle(ref: SourceRef) {
    setNotice('');
    setSelected((previous) => {
      const alreadySelected = previous.some((item) => key(item) === key(ref));
      if (alreadySelected) return previous.filter((item) => key(item) !== key(ref));
      if (previous.length >= 4) return previous;
      return [...previous, ref];
    });
  }
  /** 현재 선택한 자료로 추론 생성을 요청한다.
   * 파라미터 없음.
   * @returns 추론 요청과 결과 안내 처리가 끝나면 완료되는 Promise.
   */
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
      {error && (
        <div className="error-toast" role="alert">
          {error}
        </div>
      )}
      <div className="desk-heading">
        <div className="eyebrow">EVIDENCE CONNECTIONS</div>
        <h1>
          추론 증거<span>.</span>
        </h1>
        <p>
          열람한 증거·증언을 연결해 새로운 추론 증거를 확보하세요. 원본 자료와 수사관의 추론은
          구분해 기록합니다.
        </p>
      </div>
      <section className="panel connection-builder">
        <h3>
          <Link2 size={18} /> 자료 연결
        </h3>
        <p>
          연관된 자료 2~4개를 선택하세요. 같은 결론을 여러 근거 조합으로 도출할 수 있습니다. 추론
          증거를 다른 자료와 다시 연결할 수도 있습니다.
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
                  (selected.length >= 4 && !selected.some((ref) => key(ref) === key(item.ref)))
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
              onClick={() => navigateTo(category === 'testimony' ? 'testimonies' : 'evidence')}
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
      <DerivedList state={state} openEvidence={openEvidence} title={title} open={open} />
    </>
  );
}
