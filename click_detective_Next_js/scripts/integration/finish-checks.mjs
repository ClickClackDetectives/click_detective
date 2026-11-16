import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

/** 종결 후 변경 거절과 새 수사 초기화를 확인한다.
 * @param client 쿠키와 최신 상태를 보관하는 통합 검사 클라이언트.
 * @param session 검사에서 처음 만든 수사의 요청과 ID.
 * @returns 종결과 새 수사 검사가 끝나면 완료되는 Promise.
 */
export async function finishInvestigation(client, session) {
  const { startBody, firstId } = session;
  await client.request('notes', {
    method: 'PUT',
    body: {
      request_id: randomUUID(),
      expected_revision: client.state.revision,
      text: '종료 후',
    },
    status: 409,
  });
  client.state = (
    await client.request('start', {
      method: 'POST',
      body: { ...startBody, request_id: randomUUID() },
    })
  ).state;
  assert.notEqual(client.state.id, firstId);
  assert.equal(client.state.revision, 0);
}
