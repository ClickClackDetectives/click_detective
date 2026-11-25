import { isInvestigationId } from './contract.ts';

let accountId: string | null = null;
let homeInvestigation: string | null = null;

/** 현재 수사 페이지에 계정 수사 선택이 있으면 반환한다.
 * @returns 수사 ID, 새 수사를 뜻하는 new 또는 선택되지 않은 경우 null.
 */
export function selectedInvestigation() {
  if (typeof window === 'undefined') return null;
  if (window.location.pathname === '/game') {
    return new URLSearchParams(window.location.search).get('investigation');
  }
  return homeInvestigation;
}

/** 화면이 열릴 때 확인한 계정 범위를 보관한다.
 * @param userId 확인한 계정 ID. 로그아웃 시 null.
 * @returns 없음. 이후 수사 API에 적용할 계정을 저장한다.
 */
export function bindAccount(userId: string | null) {
  if (accountId !== userId) homeInvestigation = null;
  accountId = userId;
}

/** 현재 화면의 수사 요청이 묶인 계정과 수사를 읽는다.
 * @returns 열려 있는 계정 범위와 수사 선택.
 */
export function accountScope() {
  return { userId: accountId, investigation: selectedInvestigation() };
}

/** 로그인 없이 열 수 있는 공개 API 경로인지 확인한다.
 * @param path 브라우저 수사 API 경로.
 * @returns 공개 자료 또는 상태 확인 경로라면 true.
 */
export function isPublicApiPath(path: string) {
  const [name] = path.split(/[/?]/);
  return ['catalog', 'cases', 'assets', 'health'].includes(name);
}

/** 보호 요청에 현재 계정 범위와 수사를 명시한다.
 * @param path 브라우저 수사 API 경로.
 * @param scope 이 요청을 시작할 때 확인한 계정과 수사.
 * @returns 중계가 사용할 경로와 검색 파라미터.
 */
export function accountApiPath(path: string, scope = accountScope()) {
  const [name] = path.split(/[/?]/);
  if (isPublicApiPath(path)) return path;
  const params = new URLSearchParams();
  if (scope.investigation && name !== 'investigations' && name !== 'claim')
    params.set('investigation', scope.investigation);
  if (scope.userId) params.set('account', scope.userId);
  if (!params.size) return path;
  return path + (path.includes('?') ? '&' : '?') + params.toString();
}

/** 수사 식별자를 화면 상태 또는 직접 연 수사 주소에 기록한다.
 * @param gameId 현재 계정이 방금 열거나 생성한 수사 UUID.
 * @returns 없음. 이후 수사 요청을 고정할 식별자를 보관한다.
 */
export function selectCreatedGame(gameId: string) {
  if (typeof window === 'undefined' || !isInvestigationId(gameId)) return;
  if (window.location.pathname === '/game') {
    window.history.replaceState(window.history.state, '', '/game?investigation=' + gameId);
  } else {
    homeInvestigation = gameId;
  }
}

/** 계정 화면이 만료 상태를 표시하도록 알린다.
 * @returns 없음. 브라우저 이벤트를 발행하고 계정 범위를 지운다.
 */
export function notifySessionEnd() {
  bindAccount(null);
  if (typeof window !== 'undefined') window.dispatchEvent(new Event('cd-session-ended'));
}
