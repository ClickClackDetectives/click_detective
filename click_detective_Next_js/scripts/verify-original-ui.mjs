import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import { prepareReference, openBrowser } from './ui/reference.mjs';
import { screenshotComparer } from './ui/screenshots.mjs';
import { compareScreens } from './ui/compare-screens.mjs';
import { checkInteractions } from './ui/interactions.mjs';
import { checkSecondPhaseImages } from './ui/evidence-images.mjs';

/** 같은 상태의 비교 소스와 현재 화면을 실제 브라우저로 확인한다.
 * @param props 검사에 사용할 설정과 데이터.
 * @param props.project Next.js 프로젝트 폴더.
 * @param props.temp 검사 전용 임시 폴더.
 * @param props.base 테스트 서버의 기본 주소.
 * @param props.state 서버에서 확인한 현재 수사 상태.
 * @param props.cookies 검사 수사의 HttpOnly 쿠키 문자열.
 * @param props.start 검사 서버를 시작하는 함수.
 * @param props.ready 서버 준비를 기다리는 함수.
 * @returns 화면 비교·상호작용 검사와 보고서 저장이 끝나면 완료되는 Promise.
 */
export async function runUiChecks({ project, temp, base, state, cookies, start, ready }) {
  const refBase = await prepareReference({ project, temp, start, ready });
  const browser = await openBrowser(project);
  const report = {
    createdAt: new Date().toISOString(),
    mode: 'fixture',
    screens: [],
    checks: [],
    consoleErrors: [],
    passed: false,
  };
  const output = path.join(project, '.reports/ui');
  await mkdir(output, { recursive: true });
  try {
    const options = { viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' };
    const actualContext = await browser.newContext(options);
    const refContext = await browser.newContext(options);
    for (const context of [actualContext, refContext]) {
      await context.route(/fonts\.(googleapis|gstatic)\.com/, (route) => route.abort());
      await context.addInitScript((id) => {
        localStorage.setItem('detective-opening-v3:' + id, 'seen');
      }, state.id);
    }
    const browserCookies = [];
    for (const pair of cookies.split('; ')) {
      const index = pair.indexOf('=');
      browserCookies.push({
        name: pair.slice(0, index),
        value: pair.slice(index + 1),
        url: base,
        httpOnly: true,
        sameSite: 'Lax',
      });
    }
    await actualContext.addCookies(browserCookies);
    // 예전 로컬 API와 리팩토링 전 BFF 소스 둘 다 같은 상태로 비교한다.
    await refContext.route('**/api/game/**', (route) => route.fulfill({ json: { state } }));
    await refContext.route('**/api/detective/**', async (route) => {
      const sourceUrl = new URL(route.request().url());
      const response = await actualContext.request.get(
        base + sourceUrl.pathname + sourceUrl.search,
      );
      await route.fulfill({ response });
    });
    for (const pattern of ['**/assets/**', '**/manor.jpg']) {
      await refContext.route(pattern, async (route) => {
        const sourceUrl = new URL(route.request().url());
        const response = await actualContext.request.get(base + sourceUrl.pathname);
        await route.fulfill({ response });
      });
    }
    const actual = await actualContext.newPage();
    const original = await refContext.newPage();
    actual.on('pageerror', (error) => report.consoleErrors.push(error.message));
    await Promise.all([actual.goto(base), original.goto(refBase)]);
    await original.addStyleTag({ content: 'nextjs-portal {display:none !important}' });
    for (const page of [actual, original]) {
      await page.getByRole('button', { name: '첫 번째 사건 시작하기', exact: true }).waitFor();
    }
    const compare = screenshotComparer(actual, original, report, output);
    await compareScreens({ actual, original, compare });
    await checkSecondPhaseImages({ actual, state, report });
    await checkInteractions({ actual, actualContext, base, report });
    assert.deepEqual(report.consoleErrors, []);
    report.passed = report.screens.every((screen) => screen.exactPixels);
    assert.ok(report.passed, '일부 화면의 픽셀이 다릅니다. .reports/ui를 확인하세요.');
    console.log(
      'PASS: 비교 화면 ' +
        report.screens.length +
        '개 픽셀 일치, 상호작용 ' +
        report.checks.length +
        '개',
    );
  } finally {
    await writeFile(path.join(output, 'comparison.json'), JSON.stringify(report, null, 2));
    await browser.close();
  }
}
