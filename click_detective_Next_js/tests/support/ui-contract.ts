import fs from 'node:fs';
import path from 'node:path';
import postcss from 'postcss';
import ts from 'typescript';

/** CSS 값의 따옴표 내용은 보존하고 포맷터가 바꾼 공백만 정리한다.
 * @param value 비교할 CSS 속성 값.
 * @returns 문자열과 실제 토큰을 유지한 비교용 값.
 */
function cssValue(value: string): string {
  return value
    .split(/("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g)
    .map((part, index) => {
      if (index % 2 === 1) return part;
      return part
        .replace(/\s+/g, ' ')
        .replace(/\( /g, '(')
        .replace(/ \)/g, ')')
        .replace(/, /g, ',');
    })
    .join('');
}

/** 줄바꿈 표기를 통일하고 내부 CSS import를 펼쳐 순서가 있는 규칙 목록을 만든다.
 * @param file 현재 읽을 파일.
 * @param conditions CSS 규칙을 감싸는 조건 목록.
 * @returns 적용 조건과 순서를 보존한 CSS 규칙 목록.
 */
export function styleRules(file: string, conditions: string[] = []): unknown[] {
  const parsed = postcss.parse(fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n'));
  const entries: unknown[] = [];
  /** 현재 구문과 하위 항목을 차례로 확인한다.
   * @param nodes 순서대로 확인할 구문 목록.
   * @param context 요청 파라미터 또는 현재 CSS 조건.
   * @returns 없음. 처리 결과는 화면 상태나 검사 기록에 반영한다.
   */
  function visit(nodes: postcss.ChildNode[], context: string[]) {
    for (const node of nodes) {
      if (node.type === 'comment') continue;
      if (node.type === 'atrule' && node.name === 'import') {
        const match = node.params.match(/^['"](.+\.css)['"]$/);
        if (match) {
          entries.push(...styleRules(path.resolve(path.dirname(file), match[1]), context));
          continue;
        }
      }
      if (node.type === 'rule') {
        entries.push({
          conditions: context,
          selector: node.selector,
          declarations: node.nodes
            .filter((n) => n.type !== 'comment')
            .map((n) => {
              const declaration = n as postcss.Declaration;
              return [
                declaration.prop,
                cssValue(declaration.value),
                Boolean(declaration.important),
              ];
            }),
        });
      } else if ('nodes' in node && node.nodes) {
        const rule = node as postcss.AtRule;
        visit(rule.nodes!, [...context, '@' + rule.name + ' ' + rule.params]);
      } else {
        const rule = node as postcss.AtRule;
        entries.push({
          conditions: context,
          type: node.type,
          name: rule.name,
          params: rule.params,
        });
      }
    }
  }
  visit(parsed.nodes, conditions);
  return entries;
}

/** 화면에 사용하는 고정 문구·CSS 클래스·접근성 속성을 모은다.
 * @param folder 검사할 코드 폴더.
 * @returns 화면의 고정 문구와 접근성·스타일 속성 집합.
 */
export function uiMarkers(folder: string) {
  const texts = new Set<string>();
  const attributes = new Set<string>();
  /** 하위 폴더에서 화면 코드를 모은다.
   * @param directory 현재 확인할 폴더.
   * @returns 없음. 처리 결과는 화면 상태나 검사 기록에 반영한다.
   */
  function collect(directory: string) {
    for (const item of fs.readdirSync(directory, { withFileTypes: true })) {
      const file = path.join(directory, item.name);
      if (item.isDirectory()) {
        collect(file);
        continue;
      }
      if (!file.endsWith('.tsx')) continue;
      const source = fs.readFileSync(file, 'utf8');
      const ast = ts.createSourceFile(
        file,
        source,
        ts.ScriptTarget.Latest,
        true,
        ts.ScriptKind.TSX,
      );
      /** 현재 구문과 하위 항목을 차례로 확인한다.
       * @param node 현재 확인할 TypeScript 구문.
       * @returns 없음. 처리 결과는 화면 상태나 검사 기록에 반영한다.
       */
      function visit(node: ts.Node) {
        if (ts.isJsxText(node)) {
          const text = node.text.replace(/\s+/g, ' ').trim();
          if (text) texts.add(text);
        }
        if (ts.isJsxExpression(node) && node.expression && ts.isStringLiteral(node.expression)) {
          const text = node.expression.text.trim();
          if (text) texts.add(text);
        }
        if (ts.isJsxAttribute(node) && node.initializer && ts.isStringLiteral(node.initializer)) {
          const name = node.name.getText(ast);
          if (['className', 'aria-label', 'role', 'placeholder'].includes(name)) {
            attributes.add(name + '=' + node.initializer.text);
          }
        }
        ts.forEachChild(node, visit);
      }
      visit(ast);
    }
  }
  collect(folder);
  return { texts, attributes };
}
