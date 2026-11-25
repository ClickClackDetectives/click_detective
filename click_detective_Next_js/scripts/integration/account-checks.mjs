import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

const accessName = 'cd_access_token';
const refreshName = 'cd_refresh_token';

/** 쿠키 경로를 인식하는 별도 인증 검사 브라우저를 만든다.
 * @param base Next.js 주소.
 * @returns 쿠키를 유지하는 요청 함수와 브라우저별 쿠키 저장소.
 */
function browser(base) {
  const cookies = new Map();
  /** 브라우저 쿠키를 경로에 맞춰 전송하고 공개 응답만 반환한다.
   * @param route 같은 출처 API 경로.
   * @param props 메서드, 입력, 예상 상태, 덮어쓸 요청 헤더.
   * @returns 상태를 확인한 JSON과 응답 헤더.
   */
  async function send(route, { method = 'GET', body, status = 200, headers = {} } = {}) {
    const cookie = [...cookies]
      .filter(([, entry]) => entry.path === '/' || route.startsWith(entry.path + '/'))
      .map(([name, entry]) => name + '=' + entry.value)
      .join('; ');
    const response = await fetch(base + route, {
      method,
      headers: { cookie, origin: base, 'Content-Type': 'application/json', ...headers },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const text = await response.text();
    assert.equal(response.status, status, method + ' ' + route);
    assert.match(response.headers.get('cache-control') ?? '', /no-store/i);
    assert.doesNotMatch(text, /"(game_token|access_token|refresh_token)"\s*:/);
    const data = JSON.parse(text);
    assert.equal(Object.hasOwn(data, 'password'), false);
    if (body?.password) assert.ok(!text.includes(JSON.stringify(body.password)));
    for (const header of response.headers.getSetCookie()) {
      const [pair, ...attributes] = header.split('; ');
      const [name, value] = pair.split('=');
      assert.ok(attributes.includes('HttpOnly'));
      assert.ok(attributes.includes('SameSite=lax') || !value);
      const cookiePath = attributes.find((item) => item.startsWith('Path='))?.slice(5);
      assert.equal(cookiePath, name === refreshName ? '/api/auth' : '/');
      if (value) {
        cookies.set(name, { value, path: cookiePath });
        if (name !== 'cd_game_id') assert.ok(!text.includes(value));
      } else cookies.delete(name);
    }
    return data;
  }
  return { send, cookies };
}

/** 계정 인증, 수사 연결, 다른 브라우저 이어하기, 회전과 폐기를 검증한다.
 * @param base Next.js 서버 주소.
 * @param backend FastAPI 서버 주소.
 * @param serviceKey 이전 브라우저 수사 준비에 사용할 서버 키.
 * @returns 실제 DB를 통한 계정 통합 검사를 마치면 완료되는 Promise.
 */
export async function checkAccounts(base, backend, serviceKey) {
  const first = browser(base);
  const second = browser(base);
  const stranger = browser(base);
  const auth = '/api/auth/';
  const detective = '/api/detective/';
  const password = 'Fixture!' + randomUUID().slice(0, 6) + '1';
  const owner = { email: 'owner-' + randomUUID() + '@example.com', password };
  const outsider = { email: 'guest-' + randomUUID() + '@example.com', password };

  const catalog = await first.send(detective + 'catalog');
  const start = {
    request_id: randomUUID(),
    case_id: catalog.caseId,
    scenario_version: catalog.scenarioVersion,
  };
  const external = await stranger.send(auth + 'login', {
    method: 'POST',
    body: owner,
    status: 403,
    headers: { origin: 'https://evil.example' },
  });
  assert.equal(external.code, 'ORIGIN_REJECTED');

  const weakSignup = await first.send(auth + 'signup', {
    method: 'POST',
    body: { ...owner, password: 'lettersOnly' },
    status: 422,
  });
  assert.equal(weakSignup.code, 'INVALID_PASSWORD');
  assert.match(weakSignup.fields.password, /8~16/);
  const { user } = await first.send(auth + 'signup', { method: 'POST', body: owner, status: 201 });
  assert.equal(user.email, owner.email);
  assert.equal(first.cookies.has(accessName), false);
  await second.send(auth + 'login', { method: 'POST', body: owner });
  await stranger.send(auth + 'signup', { method: 'POST', body: outsider, status: 201 });
  await stranger.send(auth + 'login', { method: 'POST', body: outsider });
  const ownerLogin = await first.send(auth + 'login', { method: 'POST', body: owner });
  assert.deepEqual(ownerLogin.user, user);

  const legacy = await fetch(backend + '/v1/games', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + serviceKey, 'Content-Type': 'application/json' },
    body: JSON.stringify(start),
  });
  assert.equal(legacy.status, 200);
  const { state: anonymous, game_token: legacyToken } = await legacy.json();
  first.cookies.set('cd_game_id', { value: anonymous.id, path: '/' });
  first.cookies.set('cd_game_token', { value: legacyToken, path: '/' });
  assert.equal((await first.send(detective + 'state')).state, null);

  const guest = browser(base);
  for (const name of ['cd_game_id', 'cd_game_token']) {
    guest.cookies.set(name, first.cookies.get(name));
  }
  const locked = await guest.send(detective + 'state', { status: 401 });
  assert.equal(locked.code, 'ACCESS_TOKEN_MISSING');
  guest.cookies.set(accessName, { value: 'invalid-token', path: '/' });
  const invalidSession = await guest.send(detective + 'state', { status: 401 });
  assert.equal(invalidSession.code, 'ACCESS_TOKEN_INVALID');

  const claim = await first.send(detective + 'claim?account=' + user.id, {
    method: 'POST',
    body: { game_id: anonymous.id },
  });
  assert.equal(claim.game_id, anonymous.id);
  assert.equal(first.cookies.has('cd_game_token'), false);
  assert.equal(first.cookies.has(accessName), true);
  assert.deepEqual(
    await first.send(detective + 'claim?account=' + user.id, {
      method: 'POST',
      body: { game_id: anonymous.id },
    }),
    claim,
  );
  const scope = '?investigation=' + anonymous.id + '&account=' + user.id;
  const resumed = await second.send(detective + 'state' + scope);
  assert.equal(resumed.state.id, anonymous.id);
  const outside = await stranger.send(detective + 'state?investigation=' + anonymous.id, {
    status: 404,
  });
  assert.equal(outside.state, undefined);
  const list = await second.send(detective + 'investigations?limit=1');
  assert.deepEqual(
    list.items.map((item) => item.game_id),
    [anonymous.id],
  );
  assert.equal(list.next_cursor, null);

  const note = { text: '계정 수사 메모', request_id: randomUUID(), expected_revision: 0 };
  const write = await second.send(detective + 'notes' + scope, { method: 'PUT', body: note });
  const replay = await first.send(detective + 'notes' + scope, { method: 'PUT', body: note });
  assert.equal(write.state.notes, note.text);
  assert.deepEqual(replay, write);

  const created = await first.send(detective + 'start?investigation=new&account=' + user.id, {
    method: 'POST',
    body: { ...start, request_id: randomUUID() },
  });
  assert.notEqual(created.game_id, anonymous.id);
  assert.equal(created.state.id, created.game_id);
  const firstPage = await first.send(detective + 'investigations?limit=1');
  assert.ok(firstPage.next_cursor);
  const later = await first.send(
    detective + 'investigations?limit=1&cursor=' + encodeURIComponent(firstPage.next_cursor),
  );
  assert.notEqual(firstPage.items[0].game_id, later.items[0].game_id);

  const otherLogout = await stranger.send(auth + 'logout?account=' + user.id, {
    method: 'POST',
    status: 409,
  });
  assert.equal(otherLogout.code, 'ACCOUNT_CHANGED');
  assert.equal((await stranger.send(auth + 'me')).user.email, outsider.email);

  const otherGame = await stranger.send(detective + 'start', {
    method: 'POST',
    body: { ...start, request_id: randomUUID() },
  });
  const otherScope = '?investigation=' + otherGame.game_id;
  await stranger.send(detective + 'notes' + otherScope, {
    method: 'PUT',
    body: { ...note, request_id: randomUUID(), text: '다른 계정의 메모' },
  });
  assert.notEqual(otherGame.game_id, created.game_id);
  assert.equal((await stranger.send(detective + 'state')).state.notes, '다른 계정의 메모');
  assert.equal((await second.send(detective + 'state')).state.id, created.game_id);
  assert.equal((await first.send(detective + 'state')).state.notes, '');
  await stranger.send(detective + 'state?investigation=' + created.game_id, { status: 404 });

  const expired = first.cookies.get(refreshName);
  await first.send(auth + 'refresh', { method: 'POST' });
  assert.notEqual(first.cookies.get(refreshName).value, expired.value);
  const reuse = browser(base);
  reuse.cookies.set(refreshName, expired);
  await reuse.send(auth + 'refresh', { method: 'POST', status: 401 });
  await first.send(auth + 'me', { status: 401 });
  second.cookies.delete(accessName);
  await second.send(auth + 'logout', { method: 'POST' });
  assert.equal(second.cookies.has(refreshName), false);
  await second.send(auth + 'me', { status: 401 });
}
