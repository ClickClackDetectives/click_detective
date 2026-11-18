import { open } from 'node:fs/promises';
import type { Run } from '@/app/game/agent-dashboard/metrics';

/** 로그의 측정값만 숫자로 읽는다.
 * @param value 로그 값.
 * @returns 유효한 숫자 또는 null.
 */
function number(value: unknown) {
  return typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : null;
}

/** 기준 답변과 비교한 ROUGE F1 점수를 검사한다.
 * @param value 로그에 저장한 0~1 점수.
 * @returns 유효한 점수 또는 미기록.
 */
function fraction(value: unknown) {
  const score = number(value);
  return score !== null && score <= 1 ? score : undefined;
}

/** 로그의 불리언 설정을 읽는다.
 * @param value 설정값.
 * @returns 참·거짓 또는 미기록.
 */
function flag(value: unknown) {
  return typeof value === 'boolean' ? value : undefined;
}

/** 로그에서 표시 가능한 버전 또는 모델 이름을 읽는다.
 * @param value 로그 값.
 * @returns 표시 이름 또는 미기록.
 */
function label(value: unknown) {
  return typeof value === 'string' && /^[\w. /:+-]{1,80}$/.test(value) ? value : undefined;
}

/** 화면에 필요한 공개 수치와 고정 코드만 꺼낸다.
 * @param line JSONL 로그 한 줄.
 * @param index 화면 내 실행 순서.
 * @returns 표시할 실행 또는 읽을 수 없으면 null.
 */
function parseRun(line: string, index: number): Run | null {
  try {
    const trace = JSON.parse(line);
    if (!Array.isArray(trace?.events)) return null;
    const events: Run['events'] = [];
    for (const event of trace.events) {
      const stage = event?.stage;
      if (
        !['retrieval', 'generation', 'verification', 'candidate_rejected', 'failure'].includes(
          stage,
        )
      )
        continue;
      events.push({
        stage,
        ms: number(event.elapsed_ms),
        selected: number(event.selected_count) ?? undefined,
        relevanceMean: number(event.relevance_mean) ?? undefined,
        relevanceMax: number(event.relevance_max) ?? undefined,
        approved: number(event.approved_count) ?? undefined,
        required: number(event.required_count) ?? undefined,
        code:
          typeof event.code === 'string' && /^[a-z_0-9]{1,64}$/.test(event.code)
            ? event.code
            : undefined,
      });
    }
    const attempts = events.filter((event) => event.stage === 'generation').length;
    let outcome: Run['outcome'] = 'error';
    if (trace.finish_reason === 'stop') {
      outcome = attempts > 1 ? 'retried' : attempts === 1 ? 'first' : 'verified';
    }
    if (trace.finish_reason === 'fixed' || trace.finish_reason === 'fallback')
      outcome = trace.finish_reason;
    const version = [
      trace.pipeline_version,
      trace.model_version ?? trace.settings?.local_model_version,
    ]
      .filter((value) => typeof value === 'string' && /^[\w. /:+-]{1,80}$/.test(value))
      .join(' · ');
    const settings = trace.settings ?? {};
    const model = label(settings.local_model_version);
    const adapter = label(settings.adapter_version);
    const responseModel = label(trace.model_version);
    const explicitQlora = flag(settings.qlora_enabled);
    let qlora = explicitQlora;
    // 기존 로그는 실제 검증을 통과한 응답의 모델 이름에 어댑터를 덧붙인다.
    if (
      qlora === undefined &&
      trace.finish_reason === 'stop' &&
      settings.generation_mode === 'local'
    ) {
      if (model && responseModel === model) qlora = false;
      if (model && adapter && responseModel === model + '+' + adapter) qlora = true;
    }
    return {
      evaluation: {
        rouge1: fraction(trace.evaluation?.rouge1_f1),
        rouge2: fraction(trace.evaluation?.rouge2_f1),
        rougeL: fraction(trace.evaluation?.rougeL_f1),
      },
      experiment: {
        rag: flag(settings.rag_enabled),
        embedding: flag(settings.rag_embedding_enabled),
        chunking: flag(settings.rag_chunking_enabled),
        ragVersion: label(settings.rag_version) ?? label(trace.pipeline_version),
        generationVersion: label(settings.generation_version) ?? label(trace.pipeline_version),
        model,
        qlora,
        qloraInferred: explicitQlora === undefined && qlora !== undefined,
      },
      label: '최근 실행 ' + (index + 1),
      version: version || '버전 미기록',
      mode:
        trace.settings?.generation_mode === 'local'
          ? 'local'
          : trace.settings?.generation_mode === 'fixture'
            ? 'fixture'
            : '미기록',
      elapsed: number(trace.elapsed_ms),
      outcome,
      events,
    };
  } catch {
    return null;
  }
}

/** FastAPI 상태를 확인하고 공유 진단 로그의 최근 실행을 읽는다.
 * @returns 연결 상태, 표시할 안내 및 최근 실행 목록.
 */
export async function loadDashboard(): Promise<{ message: string; runs: Run[]; demo: boolean }> {
  const base = process.env.CLICK_DETECTIVE_API_URL;
  try {
    if (!base) throw new Error('missing backend');
    const response = await fetch(new URL('/healthz', base), {
      cache: 'no-store',
      signal: AbortSignal.timeout(1500),
      redirect: 'error',
    });
    if (!response.ok || (await response.json()).status !== 'ok') throw new Error('unhealthy');
  } catch {
    return { demo: true, message: 'FastAPI에 연결할 수 없어 예시 데이터를 표시합니다.', runs: [] };
  }

  const path = process.env.CLICK_DASHBOARD_TRACE_PATH;
  if (!path)
    return {
      demo: true,
      message: 'FastAPI 연결됨 · 진단 로그 경로 미설정. 예시 데이터를 표시합니다.',
      runs: [],
    };
  try {
    const file = await open(path, 'r');
    try {
      const { size } = await file.stat();
      const buffer = Buffer.alloc(Math.min(size, 512 * 1024));
      const { bytesRead } = await file.read(buffer, 0, buffer.length, size - buffer.length);
      const lines = buffer.subarray(0, bytesRead).toString('utf8').split('\n');
      if (size > buffer.length) lines.shift();
      const runs = lines
        .reverse()
        .flatMap((line, index) => {
          const run = parseRun(line, index);
          return run ? [run] : [];
        })
        .slice(0, 200);
      if (runs.length) return { demo: false, message: 'FastAPI 연결됨 · 최근 진단 로그', runs };
    } finally {
      await file.close();
    }
  } catch {
    return {
      demo: true,
      message: 'FastAPI 연결됨 · 진단 로그를 읽을 수 없어 예시 데이터를 표시합니다.',
      runs: [],
    };
  }
  return {
    demo: true,
    message: 'FastAPI 연결됨 · 기록된 실행이 없어 예시 데이터를 표시합니다.',
    runs: [],
  };
}
