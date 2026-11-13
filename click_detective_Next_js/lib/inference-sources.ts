import { evidence, suspects, type GameState, type SourceRef } from './case.ts';
export type SourceCategory = 'evidence' | 'testimony' | 'derived';
export const sourceLabels: Record<SourceCategory, string> = {
  evidence: '증거',
  testimony: '증언',
  derived: '추론',
};
/** 자료 참조를 화면용 번호·제목·보충 설명으로 변환한다. */
export function describeSource(state: GameState, ref: SourceRef) {
  return (
    state.inferenceSources.find(
      (item) => item.ref.kind === ref.kind && item.ref.id === ref.id,
    ) ?? { ref, category: ref.kind, code: ref.id, title: ref.id, context: '' }
  );
}
/** 실제 출처 후보도 서버에서 받은 목록을 사용합니다. */
export function getInferenceSources(state: GameState) {
  return state.inferenceSources;
}
/** 도출 문서의 근거 종류 이름은 서버가 계산합니다. */
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
