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
export function installLibrary(cases: LibraryCase[]) {
  caseLibrary = cases;
}
