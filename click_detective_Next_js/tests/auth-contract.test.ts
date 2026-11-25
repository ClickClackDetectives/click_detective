import test from 'node:test';
import assert from 'node:assert/strict';
import { readInvestigationPage } from '../server/proxy/investigations.ts';
import { resolveTarget } from '../server/proxy/policy.ts';
import { resolveAuthTarget, readTokenPair } from '../server/auth/contract.ts';

test('인증 중계는 지정한 메서드와 기능만 허용한다', () => {
  assert.equal(resolveAuthTarget('login', 'POST'), '/auth/login');
  assert.equal(resolveAuthTarget('login', 'GET'), null);
  assert.equal(resolveAuthTarget('../admin', 'POST'), null);
});

test('계정 수사 조회는 명시한 수사와 인증 모드를 사용한다', () => {
  const id = '74720db7-3ec9-4db8-804f-2eea975b3391';
  assert.equal(resolveTarget(['state'], 'GET', id)?.path, '/v1/games/' + id);
  assert.equal(resolveTarget(['state'], 'GET', id)?.account, true);
  assert.equal(resolveTarget(['state'], 'GET', 'invalid'), null);
  assert.equal(resolveTarget(['start'], 'POST')?.account, true);
  assert.equal(resolveTarget(['state'], 'GET')?.latest, true);
  assert.equal(resolveTarget(['notes'], 'PUT'), null);
  assert.equal(resolveTarget(['claim'], 'POST')?.account, true);
});

test('이미 만료된 인증 응답은 쿠키를 만들 수 없다', () => {
  assert.equal(
    readTokenPair({
      user: { id: 'someone', email: 'a@example.com' },
      access_token: 'access',
      refresh_token: 'refresh',
      access_expires_at: '2000-01-01T00:00:00Z',
      refresh_expires_at: '2000-01-02T00:00:00Z',
    }),
    null,
  );
});

test('수사 목록은 내부 필드를 공개하지 않는다', () => {
  const summary = {
    game_id: '74720db7-3ec9-4db8-804f-2eea975b3391',
    case_id: 'case',
    updated_at: '2026-11-25T12:00:00Z',
    revision: 1,
  };
  assert.deepEqual(
    readInvestigationPage({ items: [{ ...summary, game_token: 'private' }], next_cursor: null }),
    { items: [summary], next_cursor: null },
  );
});
