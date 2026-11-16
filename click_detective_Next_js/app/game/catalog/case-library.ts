/** 준비 중 사건 카드도 백엔드 application 응답으로 표시합니다. */
export type LibraryCase = {
  id: string;
  title: string;
  ko: string;
  desc: string;
  place: string;
  duration: string;
  level: string;
};
export let caseLibrary: LibraryCase[] = [];
/** 사건 기록실에 표시할 카드 목록을 보관한다.
 * @param cases 서버에서 받은 사건 카드 목록.
 * @returns 없음. 사건 선택 자료를 갱신한다.
 */
export function installLibrary(cases: LibraryCase[]) {
  caseLibrary = cases;
}
