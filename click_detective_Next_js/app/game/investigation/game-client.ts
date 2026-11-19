import { api, ApiError } from '../../../shared/api/client.ts';
import type { GameState } from './types';
import type { PublicCatalog } from '../catalog/types';
import { mapGameCommand } from './commands.ts';
export { requestDocument } from './documents.ts';
let latest: GameState | null = null;
let queue: Promise<unknown> = Promise.resolve();
let pending: {
  action: string;
  fingerprint: string;
  path: string;
  method: string;
  body: Record<string, unknown>;
} | null = null;
/** 응답 버전을 보관합니다. 과거 UUID의 캐시 응답으로 최신 상태를 되돌리지 않습니다.
 * @param state 서버에서 확인한 현재 수사 상태.
 * @returns 과거 응답으로 되돌리지 않은 최신 수사 상태.
 */
function accept(state: GameState | null) {
  if (!state) {
    latest = null;
    return latest;
  }
  if (!latest || state.id !== latest.id || state.revision >= latest.revision) latest = state;
  return latest;
}
/** 불확실한 통신 실패는 동일 UUID로 재확인하고 새 행동은 그 뒤에 전송합니다.
 * @param request 확인하거나 전달할 요청.
 * @returns 동일 요청의 결과로 확인한 수사 상태.
 */
async function send(request: NonNullable<typeof pending>) {
  try {
    const data = await api<{ state: GameState }>(request.path, request.method, request.body);
    pending = null;
    return accept(data.state);
  } catch (error) {
    const uncertain =
      !(error instanceof ApiError) ||
      [
        'BACKEND_UNREACHABLE',
        'BACKEND_TIMEOUT',
        'INVALID_RESPONSE',
        'operation_in_progress',
      ].includes(error.code);
    // 생성·검증 오류 응답은 백엔드가 작업 실패를 확정한 결과다.
    // 이를 pending으로 남기면 다른 질문도 이전 실패 요청에 막힌다.
    pending = uncertain ? request : null;
    if (error instanceof ApiError && error.status === 409 && !uncertain) {
      try {
        accept((await api<{ state: GameState | null }>('state')).state);
      } catch {}
    }
    throw error;
  }
}
/** 원본 화면의 요청 인터페이스입니다. 자동 저장과 심문을 직렬화해 revision 충돌을 피합니다.
 * @param action 실행할 수사 행동 이름.
 * @param body 전송할 요청 본문.
 * @returns 서버에서 확인한 최신 수사 상태 또는 null을 기다릴 Promise.
 */
export function requestGame(action: string, body?: unknown): Promise<GameState | null> {
  const task = queue
    .catch(() => {})
    .then(async () => {
      if (action === 'state')
        return accept((await api<{ state: GameState | null }>('state')).state);
      const input = (body ?? {}) as Record<string, unknown>;
      const fingerprint = JSON.stringify([action, input]);
      if (pending) {
        const same = pending.fingerprint === fingerprint;
        const recovered = await send(pending);
        if (same) return recovered;
      }
      if (action === 'start') {
        if (!input.restart && latest) return latest;
        const catalog = await api<PublicCatalog>('catalog');
        return send({
          action,
          fingerprint,
          path: 'start',
          method: 'POST',
          body: {
            request_id: crypto.randomUUID(),
            case_id: catalog.caseId,
            scenario_version: catalog.scenarioVersion,
          },
        });
      }
      if (!latest) throw new Error('먼저 수사를 시작하세요.');
      const mapped = mapGameCommand(action, input);
      return send({
        action,
        fingerprint,
        path: mapped.path,
        method: mapped.method ?? 'POST',
        body: {
          ...mapped.fields,
          request_id: crypto.randomUUID(),
          expected_revision: latest.revision,
        },
      });
    });
  queue = task;
  return task;
}
/** 오류 처리 후에도 화면이 서버에서 확인된 최신 저장 버전을 사용할 수 있게 합니다.
 * 파라미터 없음.
 * @returns 마지막으로 확인한 수사 상태 또는 null.
 */
export function currentGame() {
  return latest;
}
