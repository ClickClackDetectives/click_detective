import type { GameState } from './case';
export let accusationMinimum = 0;
export function installAccusation(minimum: number) {
  accusationMinimum = minimum;
}
/** 필수 ID는 실제 획득한 추론에 한해서 서버가 표시용으로 공개합니다. */
export function getRequiredInferenceIds(state: GameState) {
  return state.ui.requiredInferenceIds;
}
export function getAccusationReadiness(state: GameState) {
  return state.accusationReadiness;
}
