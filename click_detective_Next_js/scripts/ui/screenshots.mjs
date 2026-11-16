import path from 'node:path';

/** 글꼴과 이미지 표시가 끝날 때까지 기다린다.
 * @param page 확인할 브라우저 페이지.
 * @returns 이미지와 글꼴 준비가 끝나면 완료되는 Promise.
 */
export async function settle(page) {
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

/** 같은 상태의 두 페이지를 캡처하는 비교 함수를 만든다.
 * @param actual 현재 앱의 브라우저 페이지.
 * @param original 비교 대상의 브라우저 페이지.
 * @param report 검사 결과를 모을 객체.
 * @param output 스크린샷을 저장할 폴더.
 * @returns 화면 이름을 받아 두 페이지를 비교하는 함수.
 */
export function screenshotComparer(actual, original, report, output) {
  /** 같은 화면을 캡처하고 픽셀 일치 여부를 기록한다.
   * @param name 파일·사례·화면의 이름.
   * @returns 두 화면의 캡처와 일치 여부 기록이 끝나면 완료되는 Promise.
   */
  async function compare(name) {
    await Promise.all([settle(actual), settle(original)]);
    // 연결 사실을 안내하는 세 문구만 원본 비교 페이지에 반영합니다. 원본 소스는 수정하지 않습니다.
    await original.evaluate(() => {
      const note = document.querySelector('.demo-note p');
      if (note)
        note.textContent =
          '심문 대사는 FastAPI의 LLM 생성·검증 과정을 거쳐 전달됩니다. 연결된 백엔드의 실행 모드에 따라 실제 모델 또는 테스트 응답을 사용합니다.';
      const text = document.querySelector('.desk-heading p');
      if (text?.textContent?.includes('미리 작성한 사건 대사를 선택합니다.')) {
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

  return compare;
}
