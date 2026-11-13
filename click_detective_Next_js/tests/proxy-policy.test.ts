import test from 'node:test';
import assert from 'node:assert/strict';
import { resolveTarget, isSameOrigin } from '../lib/server/proxy-policy.ts';
import { assetUrl } from '../lib/client-api.ts';
/** 임의 URL·다른 수사 접근·다른 사이트의 변경 요청을 막는 경계를 검사합니다. */
test('허용되지 않은 경로와 경로 탈출 차단', () => {
  for (const parts of [
    ['games', 'victim'],
    ['assets', '..', 'private.json'],
    ['assets', '%2e%2e'],
    ['assets', 'a/b'],
    ['assets', 'a\\b'],
    ['unknown'],
  ])
    assert.equal(resolveTarget(parts, 'GET', 'mine'), null);
  assert.equal(resolveTarget(['notes'], 'POST', 'mine'), null);
  assert.equal(
    resolveTarget(['interrogations'], 'POST', 'mine')?.path,
    '/v1/games/mine/interrogations',
  );
  assert.equal(
    resolveTarget(['materials', 'evidence:1-01'], 'GET', 'mine')?.path,
    '/v1/games/mine/materials/evidence%3A1-01',
  );
});
test('변경 요청의 동일 출처 검사', () => {
  assert.equal(
    isSameOrigin('http://localhost:3000/api', 'http://localhost:3000'),
    true,
  );
  for (const origin of [
    null,
    'null',
    'https://evil.example',
    'http://localhost:3001',
  ])
    assert.equal(isSameOrigin('http://localhost:3000/api', origin), false);
});
test('자산을 같은 출처 API로 변환', () => {
  assert.equal(
    assetUrl('/v1/assets/manor.jpg'),
    '/api/detective/assets/manor.jpg',
  );
  assert.equal(
    assetUrl('/v1/games/any/evidence-assets/1-01'),
    '/api/detective/evidence-assets/1-01',
  );
  assert.equal(assetUrl('https://evil.example/image.png'), '');
});
