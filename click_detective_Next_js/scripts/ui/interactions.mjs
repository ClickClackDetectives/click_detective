import assert from 'node:assert/strict';

/** 새 수사·오프닝·증거 제시·심문·메모 자동 저장·복원을 확인한다.
 * @param props 검사에 사용할 설정과 데이터.
 * @param props.actual 현재 앱의 브라우저 페이지.
 * @param props.actualContext 현재 앱의 인증 쿠키를 가진 브라우저 문맥.
 * @param props.base 테스트 서버의 기본 주소.
 * @param props.report 검사 결과를 모을 객체.
 * @returns 사용자 동작 검사가 끝나면 완료되는 Promise.
 */
export async function checkInteractions({ actual, actualContext, base, report }) {
  await actual.setViewportSize({ width: 1440, height: 1000 });
  await actual.getByRole('button', { name: '다시 수사하기', exact: true }).click();
  await actual.getByRole('button', { name: '기록 초기화 후 시작' }).click();
  await actual.getByRole('button', { name: '오프닝 닫기' }).waitFor();
  await actual.getByRole('button', { name: '오프닝 닫기' }).click();
  report.checks.push('새 수사 및 오프닝 자동 표시·닫기');
  await actual
    .getByRole('navigation', { name: '수사 메뉴' })
    .getByRole('button', { name: /^증거 보관실/ })
    .click();
  await actual.locator('.evidence-card').filter({ hasText: '와인병과 잔' }).click();
  await actual.getByRole('dialog').waitFor();
  await actual.getByRole('button', { name: '심문에 증거 제시' }).click();
  assert.equal(await actual.getByRole('combobox', { name: '제시할 증거' }).inputValue(), '1-02');
  report.checks.push('자료 열람·이미지 팝업·심문에 증거 제시');
  await actual
    .getByRole('button', { name: /강민호/ })
    .first()
    .click();
  await actual
    .getByRole('textbox', { name: '용의자에게 질문' })
    .fill('와인잔과 약의 경위를 설명하세요');
  await actual.locator('form.composer').getByRole('button', { name: /질문/ }).click();
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
  await actual.getByRole('textbox', { name: '수사 메모' }).fill('브라우저 자동 저장 확인');
  await noteSaved;
  await actual.getByRole('status').filter({ hasText: '저장됨' }).waitFor();
  const saved = await (await actualContext.request.get(base + '/api/detective/state')).json();
  assert.equal(saved.state.notes, '브라우저 자동 저장 확인');
  report.checks.push('700ms 자동 저장·서버 복원');
  await actual.reload();
  await actual.getByRole('button', { name: '수사 이어하기', exact: true }).waitFor();
  await actual.getByRole('button', { name: '내 수사 기록', exact: true }).click();
  await actual
    .getByRole('navigation', { name: '수사 메뉴' })
    .getByRole('button', { name: /^수사 노트/ })
    .click();
  assert.equal(
    await actual.getByRole('textbox', { name: '수사 메모' }).inputValue(),
    '브라우저 자동 저장 확인',
  );
  report.checks.push('새로고침 후 수사·메모 복원');
}
