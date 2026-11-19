/** 데스크톱·검색·모바일 화면을 같은 순서로 전환하고 비교한다.
 * @param props 검사에 사용할 설정과 데이터.
 * @param props.actual 현재 앱의 브라우저 페이지.
 * @param props.original 비교 대상의 브라우저 페이지.
 * @param props.compare 두 화면을 캡처해 비교하는 함수.
 * @returns 전체 화면 비교가 끝나면 완료되는 Promise.
 */
export async function compareScreens({ actual, original, compare }) {
  await compare('desktop-home');
  for (const page of [actual, original])
    await page.getByRole('button', { name: '사건 기록', exact: true }).click();
  await compare('desktop-cases');
  for (const page of [actual, original])
    await page.getByRole('button', { name: '내 수사 기록', exact: true }).click();
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
    if (label === '증거 보관실') await actual.locator('.evidence-card').first().waitFor();
    if (label === '증언 기록') await actual.locator('.archive-section').first().waitFor();
    if (label === '추론 증거') await actual.locator('.connection-options label').first().waitFor();
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
  await actual.locator('.evidence-card').filter({ hasText: '와인병과 잔' }).waitFor();
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
    await page.getByRole('button', { name: '사건 기록', exact: true }).click();
  await compare('mobile-cases');
  for (const page of [actual, original])
    await page.getByRole('button', { name: '내 수사 기록', exact: true }).click();
  await compare('mobile-results');
  for (const page of [actual, original])
    await page.getByRole('button', { name: '수사 메뉴 열기' }).click();
  await compare('mobile-menu');
}
