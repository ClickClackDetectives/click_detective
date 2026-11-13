import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const project = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '..',
);
const original =
  process.env.CLICK_TEST_ORIGINAL_DIR ||
  path.resolve(project, '../share_project');
/** 원본 디자인을 의도치 않게 새 디자인으로 바꾸는 회귀를 막습니다. */
test('원본 CSS와 레이아웃을 바이트 단위로 유지', async () => {
  const files = [
    'app/globals.css',
    'app/layout.tsx',
    ...(await readdir(path.join(original, 'app/styles'))).map(
      (name) => 'app/styles/' + name,
    ),
  ];
  for (const file of files)
    assert.deepEqual(
      await readFile(path.join(project, file)),
      await readFile(path.join(original, file)),
      file,
    );
});
test('원본 홈·사건실·오프닝·팝업·노트·메뉴·타임라인 유지', async () => {
  for (const file of [
    'case-app.tsx',
    'app-header.tsx',
    'navigation.ts',
    'case-opening.tsx',
    'evidence-dialog.tsx',
    'screens/home-screen.tsx',
    'screens/cases-screen.tsx',
    'screens/notes-screen.tsx',
    'screens/timeline-screen.tsx',
    'screens/findings-screen.tsx',
  ])
    assert.deepEqual(
      await readFile(path.join(project, 'components', file)),
      await readFile(path.join(original, 'components', file)),
      file,
    );
});
