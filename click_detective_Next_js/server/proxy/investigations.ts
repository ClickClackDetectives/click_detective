import type { InvestigationSummary } from '../../shared/auth/contract.ts';
import { isInvestigationId } from '../../shared/auth/contract.ts';

/** 수사 요약에서 목록과 연결 화면에 표시할 필드만 추출한다.
 * @param data FastAPI의 수사 요약 객체.
 * @returns 공개 수사 요약. 응답 형식이 다르면 null.
 */
export function readInvestigation(data: unknown): InvestigationSummary | null {
  if (!data || typeof data !== 'object') return null;
  const item = data as Partial<InvestigationSummary>;
  const { game_id, case_id, updated_at, revision } = item;
  if (typeof game_id !== 'string' || !isInvestigationId(game_id)) return null;
  if (typeof case_id !== 'string' || !case_id) return null;
  if (typeof updated_at !== 'string' || !Number.isFinite(Date.parse(updated_at))) return null;
  if (typeof revision !== 'number' || !Number.isInteger(revision) || revision < 0) return null;
  return { game_id, case_id, updated_at, revision };
}

/** 계정 수사 목록과 다음 페이지 커서를 검증한다.
 * @param data FastAPI의 목록 응답.
 * @returns 공개 수사 요약 목록과 커서. 응답 형식이 다르면 null.
 */
export function readInvestigationPage(data: unknown) {
  if (!data || typeof data !== 'object' || !('items' in data) || !Array.isArray(data.items)) {
    return null;
  }
  if (!('next_cursor' in data)) return null;
  const cursor = data.next_cursor;
  if (cursor !== null && (typeof cursor !== 'string' || !cursor)) return null;
  const items: InvestigationSummary[] = [];
  for (const item of data.items) {
    const summary = readInvestigation(item);
    if (!summary) return null;
    items.push(summary);
  }
  return { items, next_cursor: cursor };
}
