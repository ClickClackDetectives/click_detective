import test from 'node:test';
import assert from 'node:assert/strict';
import { requestDocument } from '../app/game/investigation/documents.ts';
import { evidenceIllustrations } from '../app/game/materials/illustrations.ts';
import type { GameState } from '../app/game/investigation/types';
import { bindAccount } from '../shared/auth/scope.ts';

const userId = '74720db7-3ec9-4db8-804f-2eea975b3391';

const state = { statements: {}, derivedEvidence: {} } as GameState;

test('2차 증거의 보호된 이미지 주소를 같은 사이트의 중계 주소로 바꾼다', async (t) => {
  bindAccount(userId);
  t.after(() => bindAccount(null));
  t.mock.method(globalThis, 'fetch', async () =>
    Response.json({
      id: '2-01',
      illustration: '/v1/games/game/evidence-assets/2-01',
    }),
  );
  await requestDocument('2-01', state);
  assert.equal(
    evidenceIllustrations['2-01'],
    '/api/detective/evidence-assets/2-01?account=' + userId,
  );
  delete evidenceIllustrations['2-01'];
});

test('이미지가 null이거나 없으면 이전에 보관한 이미지 주소도 제거한다', async (t) => {
  bindAccount(userId);
  t.after(() => bindAccount(null));
  for (const illustration of [null, undefined]) {
    evidenceIllustrations['2-02'] = '/api/detective/evidence-assets/old';
    t.mock.method(globalThis, 'fetch', async () => Response.json({ id: '2-02', illustration }));
    await requestDocument('2-02', state);
    assert.equal(evidenceIllustrations['2-02'], undefined);
  }
});
