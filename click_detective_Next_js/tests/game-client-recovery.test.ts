import test from 'node:test';
import assert from 'node:assert/strict';

/** 서로 다른 테스트가 브라우저 탭의 요청 큐를 공유하지 않도록 모듈을 새로 읽습니다.
 * @param name 파일·사례·화면의 이름.
 * @returns 독립적인 요청 상태를 가진 게임 클라이언트 모듈의 Promise.
 */
async function freshClient(name: string) {
  return import(
    new URL(`../features/investigation/game-client.ts?test=${name}`, import.meta.url).href
  );
}

test('검증 실패 502 이후에는 과거 질문 대신 새 질문을 전송한다', async (t) => {
  const requests: Record<string, unknown>[] = [];
  t.mock.method(globalThis, 'fetch', async (_url: string, options: RequestInit) => {
    if (!options.body) return Response.json({ state: { id: 'game', revision: 1 } });
    const body = JSON.parse(String(options.body));
    requests.push(body);
    if (body.question === '와인잔에 무엇을 했나요?') {
      return Response.json(
        {
          error: 'Generation service failed',
          code: 'verification_evidence_mismatch',
        },
        { status: 502 },
      );
    }
    return Response.json({ state: { id: 'game', revision: 2 } });
  });
  const { requestGame } = await freshClient('definite-error');
  await requestGame('state');
  await assert.rejects(
    requestGame('interrogate', {
      suspectId: 'kang',
      question: '와인잔에 무엇을 했나요?',
    }),
  );
  await requestGame('interrogate', {
    suspectId: 'kang',
    question: '자기소개를 해주세요.',
  });
  assert.equal(requests.length, 2);
  assert.equal(requests[1].question, '자기소개를 해주세요.');
  assert.notEqual(requests[0].request_id, requests[1].request_id);
});

test('실제 통신 시간 초과는 같은 UUID를 확인한 다음 새 질문을 전송한다', async (t) => {
  const requests: Record<string, unknown>[] = [];
  t.mock.method(globalThis, 'fetch', async (_url: string, options: RequestInit) => {
    if (!options.body) return Response.json({ state: { id: 'game', revision: 1 } });
    const body = JSON.parse(String(options.body));
    requests.push(body);
    if (requests.length === 1)
      return Response.json({ error: 'timeout', code: 'BACKEND_TIMEOUT' }, { status: 504 });
    return Response.json({
      state: { id: 'game', revision: requests.length },
    });
  });
  const { requestGame } = await freshClient('uncertain-error');
  await requestGame('state');
  await assert.rejects(requestGame('interrogate', { suspectId: 'kang', question: '이전 질문' }));
  await requestGame('interrogate', { suspectId: 'kang', question: '새 질문' });
  assert.equal(requests.length, 3);
  assert.deepEqual(requests[0], requests[1]);
  assert.equal(requests[2].question, '새 질문');
  assert.equal(requests[2].expected_revision, 2);
});
