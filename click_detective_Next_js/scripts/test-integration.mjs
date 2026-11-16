import { randomUUID } from 'node:crypto';
import { mkdtemp, mkdir, writeFile, rm, access } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { IntegrationClient } from './integration/client.mjs';
import { TestServers } from './integration/servers.mjs';
import { prepareInvestigation } from './integration/api-checks.mjs';
import { completeInvestigation } from './integration/game-checks.mjs';
import { finishInvestigation } from './integration/finish-checks.mjs';

/** 사용할 백엔드 Python을 환경변수 또는 기존 가상환경에서 찾는다.
 * @param backend FastAPI 프로젝트 폴더.
 * @returns 백엔드 Python 명령 또는 실행 파일 경로.
 */
async function backendPython(backend) {
  if (process.env.CLICK_TEST_PYTHON) return process.env.CLICK_TEST_PYTHON;
  for (const name of ['.click_venv', '.venv', '.cd_venv']) {
    const candidate = path.join(backend, name, 'bin/python');
    try {
      await access(candidate);
      return candidate;
    } catch {}
  }
  return 'python3';
}

/** fixture 서버와 빌드된 Next.js를 연결하여 전체 게임을 확인한다.
 * 파라미터 없음.
 * @returns 검사와 보고서 저장 및 임시 자원 정리가 끝나면 완료되는 Promise.
 */
async function main() {
  const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const backend = path.resolve(
    process.env.CLICK_TEST_BACKEND_DIR || path.join(project, '../click_detective_FastAPI'),
  );
  const backPort = process.env.CLICK_TEST_BACKEND_PORT || '18761';
  const frontPort = process.env.CLICK_TEST_FRONTEND_PORT || '18762';
  const base = 'http://127.0.0.1:' + frontPort;
  const key = randomUUID() + randomUUID();
  const temp = await mkdtemp(path.join(tmpdir(), 'click-next-'));
  await mkdir(path.join(project, '.reports'), { recursive: true });
  const servers = new TestServers(path.join(project, '.reports/integration-server.log'));
  const client = new IntegrationClient(base, key, backend);
  let failure = null;
  try {
    servers.start(
      await backendPython(backend),
      ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', backPort],
      backend,
      {
        CLICK_API_KEY: key,
        CLICK_GENERATION_MODE: 'fixture',
        CLICK_DATABASE_PATH: path.join(temp, 'games.sqlite3'),
        CLICK_DIAGNOSTICS_ENABLED: 'false',
      },
    );
    await servers.ready('http://127.0.0.1:' + backPort + '/healthz');
    servers.start(
      process.execPath,
      ['node_modules/next/dist/bin/next', 'start', '--hostname', '127.0.0.1', '--port', frontPort],
      project,
      {
        CLICK_DETECTIVE_API_URL: 'http://127.0.0.1:' + backPort,
        CLICK_DETECTIVE_API_KEY: key,
        NEXT_TELEMETRY_DISABLED: '1',
      },
    );
    await servers.ready(base);
    const session = await prepareInvestigation(client);
    await completeInvestigation(client);
    if (process.env.CLICK_TEST_UI === '1') {
      const { runUiChecks } = await import('./verify-original-ui.mjs');
      await runUiChecks({
        project,
        backend,
        temp,
        base,
        state: client.state,
        cookies: client.cookies,
        start: servers.start.bind(servers),
        ready: servers.ready.bind(servers),
      });
    }
    await finishInvestigation(client, session);
    console.log(
      'PASS: Next.js → FastAPI HTTP ' + client.records.length + '건, 진행률·고발 점수 100',
    );
  } catch (error) {
    failure = error;
    console.error(error);
    process.exitCode = 1;
  } finally {
    const report = {
      mode: 'fixture',
      actualLlmTested: false,
      passed: !failure,
      createdAt: new Date().toISOString(),
      requests: client.records.length,
      error: failure?.message ?? null,
      records: client.records,
    };
    await writeFile(
      path.join(project, '.reports/integration.json'),
      JSON.stringify(report, null, 2),
    );
    await servers.close();
    await rm(temp, { recursive: true, force: true });
  }
}

await main();
