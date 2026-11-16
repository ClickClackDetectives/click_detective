import type { GameState, SourceRef } from '../investigation/types.ts';
export type SourceCategory = 'evidence' | 'testimony' | 'derived';
export const sourceLabels: Record<SourceCategory, string> = {
  evidence: '증거',
  testimony: '증언',
  derived: '추론',
};
/** 자료 참조를 화면용 번호·제목·보충 설명으로 변환한다.
 * @param state 서버에서 확인한 현재 수사 상태.
 * @param ref 자료 종류와 ID가 담긴 출처.
 * @returns 자료 종류·번호·제목·설명이 담긴 표시용 출처.
 */
export function describeSource(state: GameState, ref: SourceRef) {
  return (
    state.inferenceSources.find((item) => item.ref.kind === ref.kind && item.ref.id === ref.id) ?? {
      ref,
      category: ref.kind,
      code: ref.id,
      title: ref.id,
      context: '',
    }
  );
}
/** 실제 출처 후보도 서버에서 받은 목록을 사용합니다.
 * @param state 서버에서 확인한 현재 수사 상태.
 * @returns 현재 수사에서 확보한 연결 후보 목록.
 */
export function getInferenceSources(state: GameState) {
  return state.inferenceSources;
}
/** 도출 문서의 근거 종류 이름은 서버가 계산합니다.
 * @param state 서버에서 확인한 현재 수사 상태.
 * @param sources 추론을 구성한 출처 목록.
 * @returns 서버가 알려준 추론 근거 설명. 해당 설명이 없으면 기본 문구.
 */
export function getInferenceBasisLabel(state: GameState, sources: SourceRef[]) {
  return (
    state.ui.basisLabels[
      sources
        .map((s) => s.kind + ':' + s.id)
        .sort()
        .join('|')
    ] ?? '확보한 자료의 추론'
  );
}

/** 자료 종류와 ID를 합쳐 목록의 식별자를 만든다.
 * @param ref 자료 종류와 ID가 담긴 출처.
 * @returns 자료 종류와 ID를 합친 문자열.
 */
export function sourceKey(ref: SourceRef) {
  return ref.kind + ':' + ref.id;
}
