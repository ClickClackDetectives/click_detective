import { existsSync } from 'node:fs';
import { cp, mkdir, symlink } from 'node:fs/promises';
import path from 'node:path';
import { chromium } from '@playwright/test';

/** 비교할 소스의 격리된 사본을 만들고 별도 포트로 실행한다.
 * @param props 검사에 사용할 설정과 데이터.
 * @param props.project Next.js 프로젝트 폴더.
 * @param props.temp 검사 전용 임시 폴더.
 * @param props.start 검사 서버를 시작하는 함수.
 * @param props.ready 서버 준비를 기다리는 함수.
 * @returns 실행한 비교 서버 주소.
 */
export async function prepareReference({ project, temp, start, ready }) {
  const source = path.resolve(
    process.env.CLICK_TEST_ORIGINAL_DIR || path.join(project, '../share_project'),
  );
  if (!existsSync(source)) {
    throw new Error('CLICK_TEST_ORIGINAL_DIR에 비교할 UI 소스 폴더를 지정하세요.');
  }
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
  ]) {
    await cp(path.join(source, entry), path.join(reference, entry), { recursive: true });
  }
  if (existsSync(path.join(source, 'styles'))) {
    await cp(path.join(source, 'styles'), path.join(reference, 'styles'), { recursive: true });
  }
  if (existsSync(path.join(source, 'features'))) {
    await cp(path.join(source, 'features'), path.join(reference, 'features'), { recursive: true });
  }
  if (existsSync(path.join(source, 'shared'))) {
    await cp(path.join(source, 'shared'), path.join(reference, 'shared'), { recursive: true });
  }
  if (existsSync(path.join(source, 'server'))) {
    await cp(path.join(source, 'server'), path.join(reference, 'server'), { recursive: true });
  }
  await symlink(path.join(project, 'node_modules'), path.join(reference, 'node_modules'));
  if (existsSync(path.join(source, 'public'))) {
    await symlink(path.join(source, 'public'), path.join(reference, 'public'));
  }
  const port = process.env.CLICK_TEST_REFERENCE_PORT || '18763';
  const base = 'http://127.0.0.1:' + port;
  start(
    process.execPath,
    [
      path.join(project, 'node_modules/next/dist/bin/next'),
      'dev',
      '--webpack',
      '--hostname',
      '127.0.0.1',
      '--port',
      port,
    ],
    reference,
    { NEXT_TELEMETRY_DISABLED: '1', NEXT_DIST_DIR: '.next-reference' },
  );
  await ready(base);
  return base;
}

/** 같은 브라우저와 글꼴 설정으로 비교할 Chromium을 실행한다.
 * @param project Next.js 프로젝트 폴더.
 * @returns 검사에 사용할 Chromium 브라우저.
 */
export async function openBrowser(project) {
  const libraries = process.env.CLICK_TEST_BROWSER_LIBS || path.join(project, '.browser-libs');
  const env = { ...process.env };
  const fontConfig = path.join(libraries, 'fonts.conf');
  if (existsSync(fontConfig)) env.FONTCONFIG_FILE = fontConfig;
  const runtime = path.join(libraries, 'runtime/usr/lib/x86_64-linux-gnu');
  const directories = [runtime, process.env.LD_LIBRARY_PATH].filter(Boolean);
  env.LD_LIBRARY_PATH = directories.join(':');
  return chromium.launch({ headless: true, env });
}
