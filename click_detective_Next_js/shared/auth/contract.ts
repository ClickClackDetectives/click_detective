export type PublicUser = { id: string; email: string };

export type InvestigationSummary = {
  game_id: string;
  case_id: string;
  updated_at: string;
  revision: number;
};

/** UUID 형식인 수사 경로 파라미터인지 확인한다.
 * @param value 검사할 수사 식별자.
 * @returns UUID 형식이면 true.
 */
export function isInvestigationId(value: string) {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(value);
}
