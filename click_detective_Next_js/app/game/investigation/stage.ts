import type { GameState } from './types';
export let secondRoundRequirements = { inference: 0, findings: 0 };
/** 표시할 목표 개수도 백엔드 설정에서 읽습니다.
 * @param value 입력하거나 변환할 값.
 * @returns 없음. 서버가 알려준 단계 기준을 저장한다.
 */
export function installStage(value: typeof secondRoundRequirements) {
  secondRoundRequirements = value;
}
/** 서버가 알려준 2차 조사 조건을 읽는다.
 * @param state 서버에서 확인한 현재 수사 상태.
 * @returns 서버가 계산한 2차 조사 가능 여부와 부족 조건.
 */
export function getSecondRoundEligibility(state: GameState) {
  return state.secondRoundEligibility;
}
