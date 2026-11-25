import test, { type TestContext } from 'node:test';
import assert from 'node:assert/strict';
import { api } from '../shared/api/client.ts';
import { bindAccount } from '../shared/auth/scope.ts';

const owner = 'a9ed604b-e808-47c6-ac2a-f0dc510955ee';
const other = '13588fd4-6bb8-400a-a667-2db72335bc94';
const game = '74720db7-3ec9-4db8-804f-2eea975b3391';

/** 계정 수사 페이지에서 실행하는 요청의 브라우저 범위를 재현한다.
 * @param t 브라우저 상태를 테스트 종료 시 되돌릴 실행 문맥.
 * @returns 현재 계정으로 설정한 브라우저 범위의 이벤트 대상.
 */
function openAccountGame(t: TestContext) {
  const location = new URL('https://detective.example/game?investigation=' + game);
  const window = Object.assign(new EventTarget(), { location });
  const previousWindow = Object.getOwnPropertyDescriptor(globalThis, 'window');
  Object.defineProperty(globalThis, 'window', { configurable: true, value: window });
  bindAccount(owner);
  t.after(() => {
    bindAccount(null);
    if (previousWindow) Object.defineProperty(globalThis, 'window', previousWindow);
    else Reflect.deleteProperty(globalThis, 'window');
  });
  return window;
}

test('만료 후 같은 계정의 변경 요청을 같은 UUID와 본문으로 한 번 재전송한다', async (t) => {
  openAccountGame(t);
  const requests: { path: string; options: RequestInit }[] = [];
  let gameAttempts = 0;
  t.mock.method(globalThis, 'fetch', async (path: string, options: RequestInit) => {
    requests.push({ path, options });
    if (path.startsWith('/api/auth/refresh')) {
      return Response.json({ user: { id: owner, email: 'owner@example.com' } });
    }
    if (path.startsWith('/api/auth/me')) {
      return Response.json({ code: 'ACCESS_TOKEN_MISSING' }, { status: 401 });
    }
    gameAttempts += 1;
    if (gameAttempts === 1) {
      return Response.json({ code: 'ACCESS_TOKEN_EXPIRED' }, { status: 401 });
    }
    return Response.json({ state: { id: game, revision: 4 } });
  });
  const body = { request_id: 'same-request', expected_revision: 3, text: '메모' };
  assert.deepEqual(await api('notes', 'PUT', body), { state: { id: game, revision: 4 } });
  assert.equal(requests.length, 4);
  assert.deepEqual(requests[0], requests[3]);
  assert.match(requests[2].path, /account=a9ed604b-e808-47c6-ac2a-f0dc510955ee$/);
});

test('요청을 기다리는 동안 계정이 바뀌면 이전 수사 응답을 적용하지 않는다', async (t) => {
  openAccountGame(t);
  t.mock.method(globalThis, 'fetch', async () => {
    bindAccount(other);
    return Response.json({ state: { id: game, revision: 4 } });
  });
  await assert.rejects(api('state'), { code: 'ACCOUNT_CHANGED' });
});

test('갱신 결과를 잃으면 갱신을 반복하지 않고 새로 확인한 계정으로 복구한다', async (t) => {
  openAccountGame(t);
  let me = 0;
  let refresh = 0;
  let gameAttempts = 0;
  t.mock.method(globalThis, 'fetch', async (path: string) => {
    if (path.startsWith('/api/auth/me')) {
      me += 1;
      if (me === 1) return Response.json({ code: 'ACCESS_TOKEN_MISSING' }, { status: 401 });
      return Response.json({ user: { id: owner, email: 'owner@example.com' } });
    }
    if (path.startsWith('/api/auth/refresh')) {
      refresh += 1;
      throw new Error('응답 연결 종료');
    }
    gameAttempts += 1;
    if (gameAttempts === 1) {
      return Response.json({ code: 'ACCESS_TOKEN_EXPIRED' }, { status: 401 });
    }
    return Response.json({ state: { id: game } });
  });
  assert.deepEqual(await api('state'), { state: { id: game } });
  assert.equal(refresh, 1);
  assert.equal(me, 2);
  assert.equal(gameAttempts, 2);
});
