import type { GameState } from './case';
/** 진행률은 FastAPI가 계산한 값을 그대로 반환합니다. */
export function getInvestigationProgress(state: GameState) {
  return state.progress;
}
