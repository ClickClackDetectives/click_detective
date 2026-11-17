import assert from 'node:assert/strict';

/** 실제 팝업에서 2차 증거 이미지가 깨지지 않고 표시되는지 확인한다.
 * @param props 브라우저 검사에 사용할 설정.
 * @param props.actual 현재 앱의 브라우저 페이지.
 * @param props.state 전체 수사를 마친 서버 상태.
 * @param props.report 검사 결과를 기록할 객체.
 * @returns 모든 2차 증거의 이미지 확인 후 완료되는 Promise.
 */
export async function checkSecondPhaseImages({ actual, state, report }) {
  const ids = state.examined.filter((id) => /^2-\d{2}$/.test(id));
  assert.equal(ids.length, 11);
  await actual.setViewportSize({ width: 1440, height: 1000 });
  await actual
    .getByRole('navigation', { name: '수사 메뉴' })
    .getByRole('button', { name: /^증거 보관실/ })
    .click();
  for (const id of ids) {
    await actual.getByRole('textbox', { name: '증거 검색' }).fill(id);
    const card = actual.locator('.evidence-card').filter({ hasText: id });
    await card.click();
    const dialog = actual.getByRole('dialog');
    const image = dialog.locator('.evidence-illustration img');
    await image.waitFor({ state: 'visible' });
    await image.evaluate((element) => element.decode());
    assert.ok(await image.evaluate((element) => element.naturalWidth > 0), id);
    assert.ok((await image.getAttribute('src')).endsWith('/evidence-assets/' + id));
    await dialog.getByRole('button', { name: '증거 닫기', exact: true }).click();
  }
  report.checks.push('2차 조사 증거 이미지 11개 실제 표시');
  await actual.getByRole('textbox', { name: '증거 검색' }).fill('');
  await actual.getByRole('button', { name: '내 수사 기록', exact: true }).click();
}
