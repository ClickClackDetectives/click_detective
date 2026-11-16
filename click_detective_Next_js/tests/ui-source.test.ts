import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import { styleRules, uiMarkers } from './support/ui-contract.ts';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const baseline = JSON.parse(
  await readFile(path.join(project, 'tests/fixtures/ui-contract.json'), 'utf8'),
);

test('분리한 CSS의 규칙과 적용 순서를 유지한다', () => {
  const rules = styleRules(path.join(project, 'app/globals.css'));
  const actual = createHash('sha256').update(JSON.stringify(rules)).digest('hex');
  assert.equal(actual, baseline.cssSha256);
});

test('화면의 고정 문구·스타일·접근성 표식을 유지한다', () => {
  const markers = uiMarkers(path.join(project, 'features'));
  for (const text of baseline.texts) assert.ok(markers.texts.has(text), '사라진 문구: ' + text);
  for (const attribute of baseline.attributes) {
    assert.ok(markers.attributes.has(attribute), '사라진 속성: ' + attribute);
  }
});
