import type { GameState } from './types';
/** 진행률은 FastAPI가 계산한 값을 그대로 반환합니다.
 * @param state 서버에서 확인한 현재 수사 상태.
 * @returns 서버가 계산한 수사 진행률과 항목별 집계.
 */
export function getInvestigationProgress(state: GameState) {
  return state.progress;
}
