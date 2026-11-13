/** 별도 fixture FastAPI와 빌드된 Next.js를 켜서 실제 HTTP 요청·쿠키·전체 수사를 검사합니다. */
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { mkdtemp, readFile, mkdir, writeFile, rm } from 'node:fs/promises';
import { createWriteStream } from 'node:fs';
import { tmpdir } from 'node:os';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
const project = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '..',
);
const backend = path.resolve(
  process.env.CLICK_TEST_BACKEND_DIR ||
    path.join(project, '../click_detective'),
);
const backPort = process.env.CLICK_TEST_BACKEND_PORT || '18761',
  frontPort = process.env.CLICK_TEST_FRONTEND_PORT || '18762';
const base = `http://127.0.0.1:${frontPort}`,
  key = randomUUID() + randomUUID();
const temp = await mkdtemp(path.join(tmpdir(), 'click-next-'));
await mkdir(path.join(project, '.reports'), { recursive: true });
const log = createWriteStream(
  path.join(project, '.reports/integration-server.log'),
);
const children = [],
  records = [];
let cookies = '',
  state,
  failed;
function start(command, args, cwd, extra) {
  const child = spawn(command, args, {
    cwd,
    env: { ...process.env, ...extra },
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  child.stdout.pipe(log, { end: false });
  child.stderr.pipe(log, { end: false });
  children.push(child);
  child.on('error', (e) => {
    failed = e;
  });
  return child;
}
async function ready(url) {
  for (let i = 0; i < 120; i++) {
    if (failed) throw failed;
    try {
      if ((await fetch(url)).ok) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 500));
  }
  throw Error('서버 시작 대기 실패: ' + url);
}
async function request(
  route,
  { method = 'GET', body, status = 200, origin = base, headers = {} } = {},
) {
  const response = await fetch(
    base + (route.startsWith('/') ? route : '/api/detective/' + route),
    {
      method,
      headers: {
        ...(cookies ? { cookie: cookies } : {}),
        ...(method === 'GET'
          ? {}
          : { origin, 'Content-Type': 'application/json' }),
        ...headers,
      },
      ...(body ? { body: JSON.stringify(body) } : {}),
    },
  );
  const text = await response.text();
  let output;
  try {
    output = JSON.parse(text);
  } catch {
    output = {
      bytes: Buffer.byteLength(text),
      contentType: response.headers.get('content-type'),
    };
  }
  records.push({
    route,
    method,
    input: body ?? null,
    expectedStatus: status,
    status: response.status,
    output,
  });
  assert.equal(
    response.status,
    status,
    `${method} ${route}: ${text.slice(0, 500)}`,
  );
  const setCookies = response.headers.getSetCookie();
  if (setCookies.length) {
    assert.ok(setCookies.every((c) => /httponly/i.test(c)));
    cookies = setCookies.map((c) => c.split(';')[0]).join('; ');
  }
  assert.ok(!text.includes(key), '서버 키 노출');
  assert.ok(!text.includes('game_token'), '수사 토큰 본문 노출');
  return output;
}
async function act(route, fields, method = 'POST') {
  const data = await request(route, {
    method,
    body: {
      request_id: randomUUID(),
      expected_revision: state.revision,
      ...fields,
    },
  });
  state = data.state;
  return data;
}
const read = async (name) =>
  JSON.parse(await readFile(path.join(backend, 'data/case', name), 'utf8'));
try {
  start(
    path.join(backend, '.cd_venv/bin/python'),
    [
      '-m',
      'uvicorn',
      'app.main:app',
      '--host',
      '127.0.0.1',
      '--port',
      backPort,
    ],
    backend,
    {
      CLICK_API_KEY: key,
      CLICK_GENERATION_MODE: 'fixture',
      CLICK_DATABASE_PATH: path.join(temp, 'games.sqlite3'),
      CLICK_DIAGNOSTICS_ENABLED: 'false',
    },
  );
  await ready(`http://127.0.0.1:${backPort}/healthz`);
  start(
    process.execPath,
    [
      'node_modules/next/dist/bin/next',
      'start',
      '--hostname',
      '127.0.0.1',
      '--port',
      frontPort,
    ],
    project,
    {
      CLICK_DETECTIVE_API_URL: `http://127.0.0.1:${backPort}`,
      CLICK_DETECTIVE_API_KEY: key,
    },
  );
  await ready(base);
  const html = await (await fetch(base)).text();
  assert.ok(html.includes('딸깍탐정단'));
  assert.equal((await request('state')).state, null);
  const catalog = await request('catalog');
  await request('/manor.jpg');
  await request('/assets/notebook-paper.png');
  await request('/assets/intro/thirteenth-bell-opening-v3-quiet.mp4', {
    headers: { Range: 'bytes=0-99' },
    status: 206,
  });
  await request('health');
  await request('cases');
  await request('cases/' + catalog.caseId);
  await request(
    'assets/' + catalog.characters[0].portrait.slice('/v1/assets/'.length),
  );
  await request('assets/' + catalog.openingVideo.slice('/v1/assets/'.length), {
    headers: { Range: 'bytes=0-99' },
    status: 206,
  });
  await request('start', {
    method: 'POST',
    origin: 'https://evil.example',
    body: {},
    status: 403,
  });
  await request('games/other', { status: 404 });
  await request('start', { method: 'POST', body: [], status: 400 });
  const startBody = {
    request_id: randomUUID(),
    case_id: catalog.caseId,
    scenario_version: catalog.scenarioVersion,
  };
  state = (await request('start', { method: 'POST', body: startBody })).state;
  const firstId = state.id;
  assert.equal(
    (await request('start', { method: 'POST', body: startBody })).state.id,
    firstId,
  );
  await request('materials');
  await request('findings');
  await request('views/evidence');
  await request('views/testimonies');
  await request('views/inference');
  await request('materials/evidence%3A1-01', { status: 422 });
  const common = {
    request_id: randomUUID(),
    expected_revision: 0,
    evidence_id: '1-01',
  };
  const examination = await request('examinations', {
    method: 'POST',
    body: common,
  });
  state = examination.state;
  assert.deepEqual(
    await request('examinations', { method: 'POST', body: common }),
    examination,
  );
  await request('examinations', {
    method: 'POST',
    body: { ...common, evidence_id: '1-02' },
    status: 409,
  });
  await request('notes', {
    method: 'PUT',
    body: {
      request_id: randomUUID(),
      expected_revision: 0,
      text: '오래된 상태',
    },
    status: 409,
  });
  await request('materials/evidence%3A1-01');
  await request('evidence-assets/1-01');
  await act('notes', { text: 'Next.js에서 FastAPI로 저장한 메모' }, 'PUT');
  assert.equal((await request('state')).state.notes, state.notes);
  await request(
    'materials?archive_kind=evidence&search=' + encodeURIComponent('서재'),
  );
  const recordsData = (await read('evidence.json')).records,
    findings = (await read('findings.private.json')).rules,
    inferences = (await read('inferences.private.json')).rules;
  for (const phase of [1, 2]) {
    for (const record of recordsData.filter((r) => r.phase === phase))
      await act('examinations', { evidence_id: record.id });
    for (const rule of findings)
      if (
        !state.revealed.includes(rule.flag) &&
        rule.need.every((id) => state.examined.includes(id))
      )
        for (const id of rule.need)
          await act('interrogations', {
            suspect_id: rule.suspectId,
            question: '제시한 자료의 경위를 설명하세요.',
            material_id: id,
          });
    if (phase === 2)
      for (const suspect of ['cha', 'baek'])
        await act('interrogations', {
          suspect_id: suspect,
          question: '그날 밤의 동선을 설명하세요.',
          topic_id: 'movement',
        });
    const pending = inferences.filter((r) => r.phase === phase);
    while (pending.length) {
      const index = pending.findIndex((r) =>
        r.sources.every(
          (s) => s.kind !== 'derived' || state.derivedEvidence[s.id],
        ),
      );
      assert.ok(index >= 0);
      await act('inferences', { sources: pending[index].sources });
      pending.splice(index, 1);
    }
    if (phase === 1) await act('phase-transitions', { target_phase: 2 });
  }
  assert.equal(state.progress.percent, 100);
  for (const source of state.inferenceSources)
    await request(
      'materials/' + encodeURIComponent(source.ref.kind + ':' + source.ref.id),
    );
  await request('findings');
  const solution = (await read('solution.private.json')).solution;
  await act('accusations', {
    suspect_id: solution.suspectId,
    motive: solution.motive,
    method: solution.method,
    evidence_ids: Object.keys(state.derivedEvidence),
  });
  assert.equal(state.verdict.score, 100);
  assert.equal(state.verdict.correct, true);
  if (process.env.CLICK_TEST_UI === '1') {
    const { runUiChecks } = await import('./verify-original-ui.mjs');
    await runUiChecks({
      project,
      backend,
      temp,
      base,
      state,
      cookies,
      start,
      ready,
    });
  }
  await request('notes', {
    method: 'PUT',
    body: {
      request_id: randomUUID(),
      expected_revision: state.revision,
      text: '종료 후',
    },
    status: 409,
  });
  state = (
    await request('start', {
      method: 'POST',
      body: { ...startBody, request_id: randomUUID() },
    })
  ).state;
  assert.notEqual(state.id, firstId);
  assert.equal(state.revision, 0);
  console.log(
    `PASS: 실제 Next.js → FastAPI HTTP ${records.length}건, 전체 수사 진행률·고발 점수 100`,
  );
} catch (error) {
  failed = error;
  console.error(error);
  process.exitCode = 1;
} finally {
  await writeFile(
    path.join(project, '.reports/integration.json'),
    JSON.stringify(
      {
        mode: 'fixture',
        actualLlmTested: false,
        passed: !failed,
        createdAt: new Date().toISOString(),
        requests: records.length,
        error: failed?.message ?? null,
        records,
      },
      null,
      2,
    ),
  );
  for (const child of children.reverse()) {
    child.kill('SIGTERM');
    await Promise.race([
      new Promise((r) => child.once('exit', r)),
      new Promise((r) => setTimeout(r, 3000)),
    ]);
    if (child.exitCode === null) child.kill('SIGKILL');
  }
  log.end();
  await rm(temp, { recursive: true, force: true });
}
