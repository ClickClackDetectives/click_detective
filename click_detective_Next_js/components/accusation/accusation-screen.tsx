import { ArrowRight, CheckCheck, Gavel } from 'lucide-react';
import { suspects, motiveOptions, methodOptions } from '@/app/game/catalog/catalog';
import type { GameState } from '@/app/game/investigation/types';
import type { CaseGameController } from '@/app/game/investigation/use-case-game';

type Props = Omit<
  Pick<CaseGameController, 'state' | 'form' | 'setForm' | 'setModal' | 'busy' | 'navigateTo'>,
  'state'
> & { state: GameState };

/** 미종결 수사라면 준비도와 무관하게 고발 폼을 열고 근거는 선택 사항으로 받습니다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.form 고발 대상·동기·방법·근거 입력.
 * @param props.setForm 고발 입력값을 바꾸는 함수.
 * @param props.setModal 안내 팝업을 열거나 닫는 함수.
 * @param props.busy 요청 처리 중인지 여부.
 * @param props.navigateTo 선택한 화면으로 이동하는 함수.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function AccusationScreen({ state, form, setForm, setModal, busy, navigateTo }: Props) {
  return (
    <>
      <div className="desk-heading">
        <div className="eyebrow">CLOSE THE CASE</div>
        <h1>
          당신의 결론은 무엇입니까<span>?</span>
        </h1>
        <p>
          조사 단계와 진행도에 관계없이 고발할 수 있습니다. 확보한 추론 증거를 선택해 결론을
          뒷받침하세요. 제출하면 수사가 종결됩니다.
        </p>
      </div>
      {state.verdict ? (
        <div className="panel empty">
          <CheckCheck size={35} />
          <h2>이 사건은 종결되었습니다.</h2>
          <button className="primary" onClick={() => navigateTo('results')}>
            수사 결과 보기 <ArrowRight size={16} />
          </button>
        </div>
      ) : (
        <form
          className="accusation"
          onSubmit={(e) => {
            e.preventDefault();
            setModal('confirm');
          }}
        >
          <div className="phase-notice">
            <div>
              <strong>제출 전 확인</strong>
              <p>추론 증거 없이도 제출할 수 있습니다. 근거가 부족하면 입증 평가에 반영됩니다.</p>
            </div>
          </div>
          <div className="form-grid">
            <label>
              <span>01 · 범인</span>
              <select
                required
                value={form.suspectId}
                onChange={(e) => setForm({ ...form, suspectId: e.target.value })}
              >
                <option value="">용의자를 선택하세요</option>
                {suspects.map((s) => (
                  <option value={s.id} key={s.id}>
                    {s.name} · {s.role}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>02 · 동기</span>
              <select
                required
                value={form.motive}
                onChange={(e) => setForm({ ...form, motive: e.target.value })}
              >
                <option value="">범행 동기를 선택하세요</option>
                {motiveOptions.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span>03 · 수단</span>
              <select
                required
                value={form.method}
                onChange={(e) => setForm({ ...form, method: e.target.value })}
              >
                <option value="">범행 수단을 선택하세요</option>
                {methodOptions.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="evidence-selection">
            <h3>
              04 · 제출할 추론 증거 <small>선택 사항</small>
            </h3>
            {Object.keys(state.derivedEvidence).length === 0 && (
              <p>확보한 추론 증거가 없습니다. 증거를 선택하지 않고도 제출할 수 있습니다.</p>
            )}
            {Object.values(state.derivedEvidence)
              .filter((e) => e.phase <= state.phase)
              .map((e) => (
                <label key={e.id}>
                  <input
                    type="checkbox"
                    checked={form.evidenceIds.includes(e.id)}
                    onChange={(ev) =>
                      setForm({
                        ...form,
                        evidenceIds: ev.target.checked
                          ? [...form.evidenceIds, e.id]
                          : form.evidenceIds.filter((x) => x !== e.id),
                      })
                    }
                  />
                  <span className="mono">{e.code}</span>
                  <span>{e.title}</span>
                </label>
              ))}
          </div>
          <div className="accusation-bottom">
            <p>
              고발을 제출하면 수사가 종결됩니다.
              <br />
              모든 기록을 검토한 뒤 결정하세요.
            </p>
            <button className="primary" disabled={busy}>
              <Gavel size={16} />
              최종 고발 제출 <ArrowRight size={16} />
            </button>
          </div>
        </form>
      )}
    </>
  );
}
