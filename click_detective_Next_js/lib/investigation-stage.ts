import type { GameState } from './case';
export let secondRoundRequirements = { inference: 0, findings: 0 };
/** 표시할 목표 개수도 백엔드 설정에서 읽습니다. */
export function installStage(value: typeof secondRoundRequirements) {
  secondRoundRequirements = value;
}
export function getSecondRoundEligibility(state: GameState) {
  return state.secondRoundEligibility;
}
