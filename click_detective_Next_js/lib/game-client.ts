import { api, ApiError, assetUrl } from './client-api.ts';
import type { GameState, PublicCatalog } from './case';
import { evidenceIllustrations } from './evidence-illustrations.ts';
import type { InvestigationDocument } from './investigation-documents';
let latest: GameState | null = null;
let queue: Promise<unknown> = Promise.resolve();
let pending: {
  action: string;
  fingerprint: string;
  path: string;
  method: string;
  body: Record<string, unknown>;
} | null = null;
/** 화면의 기존 행동 이름을 FastAPI 계약으로 바꿉니다. 규칙을 판정하지 않습니다. */
function command(action: string, input: Record<string, unknown>) {
  switch (action) {
    case 'examine':
      return {
        path: 'examinations',
        fields: { evidence_id: input.evidenceId },
      };
    case 'interrogate':
      return {
        path: 'interrogations',
        fields: {
          suspect_id: input.suspectId,
          question: input.question,
          ...(input.topicId ? { topic_id: input.topicId } : {}),
          ...(input.evidenceId ? { material_id: input.evidenceId } : {}),
        },
      };
    case 'connect-evidence':
      return { path: 'inferences', fields: { sources: input.sources } };
    case 'advance':
      return { path: 'phase-transitions', fields: { target_phase: 2 } };
    case 'notes':
      return { path: 'notes', method: 'PUT', fields: { text: input.text } };
    case 'accuse':
      return {
        path: 'accusations',
        fields: {
          suspect_id: input.suspectId,
          motive: input.motive,
          method: input.method,
          evidence_ids: input.evidenceIds,
        },
      };
    default:
      throw new Error('지원하지 않는 수사 행동입니다.');
  }
}
/** 응답 버전을 보관합니다. 과거 UUID의 캐시 응답으로 최신 상태를 되돌리지 않습니다. */
function accept(state: GameState | null) {
  if (!state) {
    latest = null;
    return latest;
  }
  if (!latest || state.id !== latest.id || state.revision >= latest.revision)
    latest = state;
  return latest;
}
/** 불확실한 통신 실패는 동일 UUID로 재확인하고 새 행동은 그 뒤에 전송합니다. */
async function send(request: NonNullable<typeof pending>) {
  try {
    const data = await api<{ state: GameState }>(
      request.path,
      request.method,
      request.body,
    );
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
/** 원본 화면의 요청 인터페이스입니다. 자동 저장과 심문을 직렬화해 revision 충돌을 피합니다. */
export function requestGame(
  action: string,
  body?: unknown,
): Promise<GameState | null> {
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
      const mapped = command(action, input);
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
/** 오류 처리 후에도 화면이 서버에서 확인된 최신 저장 버전을 사용할 수 있게 합니다. */
export function currentGame() {
  return latest;
}
/** 원본 팝업의 문서 형태를 서버 상세 응답에서 만듭니다. 본문은 미리 번들에 넣지 않습니다. */
export async function requestDocument(
  id: string,
  state: GameState,
): Promise<InvestigationDocument> {
  const kind = state.derivedEvidence[id]
    ? 'derived'
    : state.statements[id]
      ? 'testimony'
      : 'evidence';
  const data = await api<
    InvestigationDocument & {
      excerpt?: string;
      illustration?: string;
      nature?: string;
      time?: string;
      source?: { file: string; pages: number[]; section: string };
      speaker?: string;
      messageIndex?: number;
    }
  >('materials/' + encodeURIComponent(kind + ':' + id));
  if (data.illustration)
    evidenceIllustrations[id] = assetUrl(data.illustration);
  if (kind === 'testimony') {
    const { suspects } = await import('./case');
    const speaker = suspects.find((p) => p.id === data.speaker)?.name;
    const heading = data.nature + (data.time ? ' · ' + data.time : '');
    const answer =
      state.messages[data.messageIndex ?? -1]?.text ?? data.excerpt;
    const source = data.source
      ? `출처: ${data.source.file} · ${data.source.pages.join(', ')}쪽 · ${data.source.section}`
      : '';
    return {
      ...data,
      type: data.nature ?? '증언',
      body: [speaker, heading, answer, source].filter(Boolean).join('\n\n'),
    };
  }
  return data;
}
