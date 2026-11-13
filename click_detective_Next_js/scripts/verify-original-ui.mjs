/** 격리된 원본 사본과 실제 FastAPI 연결 UI를 동일 상태·해상도로 열어 화면과 상호작용을 비교합니다. */
import { existsSync } from 'node:fs';
import { chromium } from '@playwright/test';
import { cp, mkdir, readFile, writeFile, symlink } from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';

export async function runUiChecks({
  project,
  temp,
  base,
  state,
  cookies,
  start,
  ready,
}) {
  const source = path.resolve(
    process.env.CLICK_TEST_ORIGINAL_DIR ||
      path.join(project, '../share_project'),
  );
  const reference = path.join(temp, 'reference');
  await mkdir(reference);
  for (const entry of [
    'app',
    'components',
    'hooks',
    'lib',
    'package.json',
    'tsconfig.json',
    'next.config.ts',
  ])
    await cp(path.join(source, entry), path.join(reference, entry), {
      recursive: true,
    });
  await symlink(
    path.join(source, 'node_modules'),
    path.join(reference, 'node_modules'),
  );
  await symlink(path.join(source, 'public'), path.join(reference, 'public'));
  const refPort = process.env.CLICK_TEST_REFERENCE_PORT || '18763';
  const refBase = `http://127.0.0.1:${refPort}`;
  start(
    process.execPath,
    [
      path.join(source, 'node_modules/next/dist/bin/next'),
      'dev',
      '--webpack',
      '--hostname',
      '127.0.0.1',
      '--port',
      refPort,
    ],
    reference,
    { NEXT_TELEMETRY_DISABLED: '1' },
  );
  await ready(refBase);
  const browser = await chromium.launch({
    headless: true,
    env: {
      ...process.env,
      ...(existsSync(path.join(project, '.browser-libs/fonts.conf'))
        ? { FONTCONFIG_FILE: path.join(project, '.browser-libs/fonts.conf') }
        : {}),
      LD_LIBRARY_PATH: [
        path.join(project, '.browser-libs/runtime/usr/lib/x86_64-linux-gnu'),
        process.env.LD_LIBRARY_PATH,
      ]
        .filter(Boolean)
        .join(':'),
    },
  });
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
    const actualContext = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
      reducedMotion: 'reduce',
    });
    const refContext = await browser.newContext({
      viewport: { width: 1440, height: 1000 },
      reducedMotion: 'reduce',
    });
    for (const context of [actualContext, refContext]) {
      await context.route(/fonts\.(googleapis|gstatic)\.com/, (route) =>
        route.abort(),
      );
      await context.addInitScript((id) => {
        localStorage.setItem('detective-opening-v3:' + id, 'seen');
      }, state.id);
    }
    await actualContext.addCookies(
      cookies.split('; ').map((pair) => {
        const i = pair.indexOf('=');
        return {
          name: pair.slice(0, i),
          value: pair.slice(i + 1),
          url: base,
          httpOnly: true,
          sameSite: 'Lax',
        };
      }),
    );
    await refContext.route('**/api/game/**', (route) =>
      route.fulfill({ json: { state } }),
    );
    const actual = await actualContext.newPage(),
      original = await refContext.newPage();
    actual.on('pageerror', (e) => report.consoleErrors.push(e.message));
    await Promise.all([actual.goto(base), original.goto(refBase)]);
    await original.addStyleTag({
      content: 'nextjs-portal {display:none !important}',
    });
    await Promise.all([
      actual
        .getByRole('button', { name: '첫 번째 사건 시작하기', exact: true })
        .waitFor(),
      original
        .getByRole('button', { name: '첫 번째 사건 시작하기', exact: true })
        .waitFor(),
    ]);
    async function settle(page) {
      await page.waitForTimeout(250);
      await page.evaluate(async () => {
        await document.fonts.ready;
        await Promise.all(
          Array.from(document.images).map((img) =>
            img.complete
              ? Promise.resolve()
              : new Promise((resolve) => {
                  img.onload = resolve;
                  img.onerror = resolve;
                }),
          ),
        );
      });
    }
    async function compare(name) {
      await Promise.all([settle(actual), settle(original)]);
      // 연결 사실을 안내하는 세 문구만 원본 비교 페이지에 반영합니다. 원본 소스는 수정하지 않습니다.
      await original.evaluate(() => {
        const note = document.querySelector('.demo-note p');
        if (note)
          note.textContent =
            '심문 대사는 FastAPI의 LLM 생성·검증 과정을 거쳐 전달됩니다. 연결된 백엔드의 실행 모드에 따라 실제 모델 또는 테스트 응답을 사용합니다.';
        const text = document.querySelector('.desk-heading p');
        if (
          text?.textContent?.includes('미리 작성한 사건 대사를 선택합니다.')
        ) {
          text.firstChild.textContent =
            '이름·동선·목격 사실·증거를 물어보세요. FastAPI에서 생성하고 검증한 대사를 받습니다. ';
          text.querySelector('.subtle').textContent = 'FastAPI 연결';
        }
      });
      const [a, b] = await Promise.all([
        actual.screenshot({
          path: path.join(output, name + '-actual.png'),
          fullPage: true,
          animations: 'disabled',
        }),
        original.screenshot({
          path: path.join(output, name + '-original.png'),
          fullPage: true,
          animations: 'disabled',
        }),
      ]);
      const match = a.equals(b);
      report.screens.push({ name, exactPixels: match });
    }
    await compare('desktop-home');
    for (const page of [actual, original])
      await page
        .getByRole('button', { name: '사건 기록', exact: true })
        .click();
    await compare('desktop-cases');
    for (const page of [actual, original])
      await page
        .getByRole('button', { name: '내 수사 기록', exact: true })
        .click();
    await compare('desktop-results');
    const menus = [
      '사건 브리핑',
      '증거 보관실',
      '증언 기록',
      '용의자 심문',
      '발견한 쟁점',
      '추론 증거',
      '사건 타임라인',
      '수사 노트',
      '최종 고발',
    ];
    for (const [index, label] of menus.entries()) {
      for (const page of [actual, original])
        await page
          .getByRole('navigation', { name: '수사 메뉴' })
          .getByRole('button', { name: new RegExp('^' + label) })
          .click();
      if (label === '증거 보관실')
        await actual.locator('.evidence-card').first().waitFor();
      if (label === '증언 기록')
        await actual.locator('.archive-section').first().waitFor();
      if (label === '추론 증거')
        await actual.locator('.connection-options label').first().waitFor();
      await compare('desktop-' + index);
    }
    // 검색·분류 버튼은 원본과 같은 결과와 화면을 보여야 합니다.
    for (const page of [actual, original]) {
      await page
        .getByRole('navigation', { name: '수사 메뉴' })
        .getByRole('button', { name: /^증거 보관실/ })
        .click();
      await page.getByRole('textbox', { name: '증거 검색' }).fill('와인');
    }
    await actual
      .locator('.evidence-card')
      .filter({ hasText: '와인병과 잔' })
      .waitFor();
    await compare('desktop-evidence-search');
    for (const page of [actual, original]) {
      await page
        .getByRole('navigation', { name: '수사 메뉴' })
        .getByRole('button', { name: /^증언 기록/ })
        .click();
      await page.getByRole('textbox', { name: '증언 검색' }).fill('강민호');
    }
    await actual.getByRole('region', { name: '강민호', exact: true }).waitFor();
    await compare('desktop-testimony-search');
    for (const page of [actual, original]) {
      await page.setViewportSize({ width: 390, height: 844 });
      await page.getByRole('button', { name: '딸깍탐정단 홈' }).click();
    }
    await compare('mobile-home');
    for (const page of [actual, original])
      await page
        .getByRole('button', { name: '사건 기록', exact: true })
        .click();
    await compare('mobile-cases');
    for (const page of [actual, original])
      await page
        .getByRole('button', { name: '내 수사 기록', exact: true })
        .click();
    await compare('mobile-results');
    for (const page of [actual, original])
      await page.getByRole('button', { name: '수사 메뉴 열기' }).click();
    await compare('mobile-menu');
    // 실제 FastAPI에 연결한 화면에서 새 수사·열람·메모 자동 저장·심문·팝업·영상 UX를 검사합니다.
    await actual.setViewportSize({ width: 1440, height: 1000 });
    await actual
      .getByRole('button', { name: '다시 수사하기', exact: true })
      .click();
    await actual.getByRole('button', { name: '기록 초기화 후 시작' }).click();
    await actual.getByRole('button', { name: '오프닝 닫기' }).waitFor();
    await actual.getByRole('button', { name: '오프닝 닫기' }).click();
    report.checks.push('새 수사 및 오프닝 자동 표시·닫기');
    await actual
      .getByRole('navigation', { name: '수사 메뉴' })
      .getByRole('button', { name: /^증거 보관실/ })
      .click();
    await actual
      .locator('.evidence-card')
      .filter({ hasText: '와인병과 잔' })
      .click();
    await actual.getByRole('dialog').waitFor();
    await actual.getByRole('button', { name: '심문에 증거 제시' }).click();
    assert.equal(
      await actual.getByRole('combobox', { name: '제시할 증거' }).inputValue(),
      '1-02',
    );
    report.checks.push('자료 열람·이미지 팝업·심문에 증거 제시');
    await actual
      .getByRole('button', { name: /강민호/ })
      .first()
      .click();
    await actual
      .getByRole('textbox', { name: '용의자에게 질문' })
      .fill('와인잔과 약의 경위를 설명하세요');
    await actual
      .locator('form.composer')
      .getByRole('button', { name: /질문/ })
      .click();
    await actual.locator('.message.suspect').last().waitFor();
    assert.ok(!(await actual.locator('.error-toast').count()));
    report.checks.push('자료 첨부 심문 실제 API 요청·응답 표시');
    await actual
      .getByRole('navigation', { name: '수사 메뉴' })
      .getByRole('button', { name: /^수사 노트/ })
      .click();
    const noteSaved = actual.waitForResponse(
      (response) =>
        response.url().endsWith('/api/detective/notes') &&
        response.request().method() === 'PUT' &&
        response.status() === 200,
    );
    await actual
      .getByRole('textbox', { name: '수사 메모' })
      .fill('브라우저 자동 저장 확인');
    await noteSaved;
    await actual.getByRole('status').filter({ hasText: '저장됨' }).waitFor();
    const saved = await (
      await actualContext.request.get(base + '/api/detective/state')
    ).json();
    assert.equal(saved.state.notes, '브라우저 자동 저장 확인');
    report.checks.push('700ms 자동 저장·서버 복원');
    await actual.reload();
    await actual
      .getByRole('button', { name: '수사 이어하기', exact: true })
      .waitFor();
    await actual
      .getByRole('button', { name: '내 수사 기록', exact: true })
      .click();
    await actual
      .getByRole('navigation', { name: '수사 메뉴' })
      .getByRole('button', { name: /^수사 노트/ })
      .click();
    assert.equal(
      await actual.getByRole('textbox', { name: '수사 메모' }).inputValue(),
      '브라우저 자동 저장 확인',
    );
    report.checks.push('새로고침 후 수사·메모 복원');
    assert.deepEqual(report.consoleErrors, []);
    report.passed = report.screens.every((s) => s.exactPixels);
    assert.ok(
      report.passed,
      '일부 화면의 픽셀이 원본과 다릅니다. .reports/ui를 확인하세요.',
    );
    console.log(
      `PASS: 원본 대비 화면 ${report.screens.length}개 픽셀 일치, 브라우저 상호작용 ${report.checks.length}개`,
    );
  } finally {
    await writeFile(
      path.join(output, 'comparison.json'),
      JSON.stringify(report, null, 2),
    );
    await browser.close();
  }
}
