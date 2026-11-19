import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

/** API 인증·자산·쿠키·중복·버전·검색을 확인하고 수사를 준비한다.
 * @param client 쿠키와 최신 상태를 보관하는 통합 검사 클라이언트.
 * @returns 처음 생성한 수사 요청과 ID.
 */
export async function prepareInvestigation(client) {
  const html = await (await fetch(client.base)).text();
  assert.ok(html.includes('딸깍탐정단'));
  assert.equal((await client.request('state')).state, null);
  const catalog = await client.request('catalog');
  await client.request('/manor.jpg');
  await client.request('/assets/notebook-paper.png');
  await client.request('/assets/intro/thirteenth-bell-opening-v3-quiet.mp4', {
    headers: { Range: 'bytes=0-99' },
    status: 206,
  });
  await client.request('health');
  await client.request('cases');
  await client.request('cases/' + catalog.caseId);
  await client.request('assets/' + catalog.characters[0].portrait.slice('/v1/assets/'.length));
  await client.request('assets/' + catalog.openingVideo.slice('/v1/assets/'.length), {
    headers: { Range: 'bytes=0-99' },
    status: 206,
  });
  await client.request('start', {
    method: 'POST',
    origin: 'https://evil.example',
    body: {},
    status: 403,
  });
  await client.request('games/other', { status: 404 });
  await client.request('start', { method: 'POST', body: [], status: 400 });
  const startBody = {
    request_id: randomUUID(),
    case_id: catalog.caseId,
    scenario_version: catalog.scenarioVersion,
  };
  client.state = (await client.request('start', { method: 'POST', body: startBody })).state;
  const firstId = client.state.id;
  assert.equal(
    (await client.request('start', { method: 'POST', body: startBody })).state.id,
    firstId,
  );
  await client.request('materials');
  await client.request('findings');
  await client.request('views/evidence');
  await client.request('views/testimonies');
  await client.request('views/inference');
  await client.request('materials/evidence%3A1-01', { status: 422 });
  const common = {
    request_id: randomUUID(),
    expected_revision: 0,
    evidence_id: '1-01',
  };
  const examination = await client.request('examinations', {
    method: 'POST',
    body: common,
  });
  client.state = examination.state;
  assert.deepEqual(
    await client.request('examinations', { method: 'POST', body: common }),
    examination,
  );
  await client.request('examinations', {
    method: 'POST',
    body: { ...common, evidence_id: '1-02' },
    status: 409,
  });
  await client.request('notes', {
    method: 'PUT',
    body: {
      request_id: randomUUID(),
      expected_revision: 0,
      text: '오래된 상태',
    },
    status: 409,
  });
  await client.request('materials/evidence%3A1-01');
  await client.request('evidence-assets/1-01');
  await client.act('notes', { text: 'Next.js에서 FastAPI로 저장한 메모' }, 'PUT');
  assert.equal((await client.request('state')).state.notes, client.state.notes);
  await client.request('materials?archive_kind=evidence&search=' + encodeURIComponent('서재'));

  return { startBody, firstId };
}
