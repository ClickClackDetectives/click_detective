import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import ts from 'typescript';

const roots = [
  'app',
  'styles',
  'shared',
  'server',
  'components',
  'hooks',
  'lib',
  'scripts',
  'tests',
];

/** 검사할 소스 파일을 하위 폴더까지 찾는다.
 * @param folder 현재 확인할 폴더.
 * @returns TypeScript·JavaScript·CSS 파일 경로 목록.
 */
function sourceFiles(folder: string): string[] {
  const files: string[] = [];
  for (const item of fs.readdirSync(folder, { withFileTypes: true })) {
    const file = path.join(folder, item.name);
    if (item.isDirectory()) files.push(...sourceFiles(file));
    else if (/\.(ts|tsx|mjs|css)$/.test(file)) files.push(file);
  }
  return files;
}

const files = [...roots.flatMap(sourceFiles), 'next.config.ts'];

test('각 소스 파일은 설명 주석을 포함하여 250줄 이내다', () => {
  for (const file of files) {
    const lines = fs.readFileSync(file, 'utf8').trimEnd().split('\n').length;
    assert.ok(lines <= 250, `${file}: ${lines}줄`);
  }
});

test('이름 있는 함수·클래스에는 파라미터와 반환값 설명이 있다', () => {
  for (const file of files.filter((file) => !file.endsWith('.css'))) {
    const source = fs.readFileSync(file, 'utf8');
    const ast = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true);
    /** 구현이 있는 이름 붙은 함수와 클래스를 확인한다.
     * @param node 검사할 TypeScript 구문.
     * @returns 없음. 설명 누락을 발견하면 검사를 실패시킨다.
     */
    function visit(node: ts.Node) {
      const declaration = ts.isFunctionDeclaration(node) || ts.isClassDeclaration(node);
      const method = ts.isMethodDeclaration(node) || ts.isConstructorDeclaration(node);
      const arrow =
        ts.isVariableDeclaration(node) &&
        node.initializer &&
        (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer));
      if ((declaration && node.name) || (method && node.body) || arrow) {
        const owner = arrow ? node.parent.parent : node;
        const comments = ts.getLeadingCommentRanges(source, owner.getFullStart()) ?? [];
        const doc =
          comments
            .map((range) => source.slice(range.pos, range.end))
            .findLast((comment) => comment.startsWith('/**')) ?? '';
        const location = `${file}: ${node.getText(ast).split('\n')[0]}`;
        assert.ok(doc.includes('@returns'), '반환값 설명 누락: ' + location);
        const fn = arrow ? node.initializer! : node;
        if ('parameters' in fn) {
          for (const parameter of (fn as ts.FunctionLikeDeclaration).parameters) {
            const name = ts.isIdentifier(parameter.name) ? parameter.name.text : 'props';
            assert.ok(
              new RegExp('@param ' + name + '(?:\\s|\\.)').test(doc),
              '파라미터 설명 누락: ' + name + ' / ' + location,
            );
          }
        }
      }
      ts.forEachChild(node, visit);
    }
    visit(ast);
  }
});
