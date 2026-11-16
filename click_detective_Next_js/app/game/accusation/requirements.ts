import type { GameState } from '../investigation/types';
export let accusationMinimum = 0;
/** 고발 준비도에 표시할 서버 기준을 보관한다.
 * @param minimum 서버가 알려준 고발 준비 표시 기준.
 * @returns 없음. 서버의 고발 표시 기준을 저장한다.
 */
export function installAccusation(minimum: number) {
  accusationMinimum = minimum;
}
/** 필수 ID는 실제 획득한 추론에 한해서 서버가 표시용으로 공개합니다.
 * @param state 서버에서 확인한 현재 수사 상태.
 * @returns 고발 근거에 필요한 확보 추론의 ID 목록.
 */
export function getRequiredInferenceIds(state: GameState) {
  return state.ui.requiredInferenceIds;
}
/** 서버가 알려준 고발 준비 상태를 읽는다.
 * @param state 서버에서 확인한 현재 수사 상태.
 * @returns 서버가 계산한 고발 준비도와 안내 정보.
 */
export function getAccusationReadiness(state: GameState) {
  return state.accusationReadiness;
}
