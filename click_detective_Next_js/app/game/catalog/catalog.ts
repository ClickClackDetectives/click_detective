import type { CaseInfo, PublicCatalog, Person, EvidenceRecord } from './types';
import type { TimelineEntry } from '../investigation/types';

export let caseInfo: CaseInfo;

export let suspects: Person[] = [];

export let evidence: EvidenceRecord[] = [];

export let motiveOptions: { id: string; label: string }[] = [];

export let methodOptions: { id: string; label: string }[] = [];

export let questionLimit = 0;

export let revelationCount = 0;

export let publicTimeline: TimelineEntry[] = [];

/** 브라우저가 초기 카탈로그를 받은 후 원본 화면의 읽기 전용 표시 자료를 준비합니다.
 * @param data 서버에서 받은 공개 자료.
 * @returns 없음. 카탈로그 표시 자료를 갱신한다.
 */
export function installCatalog(data: PublicCatalog) {
  caseInfo = data.case;
  suspects = data.characters;
  evidence = data.display.evidence;
  motiveOptions = data.motiveOptions;
  methodOptions = data.methodOptions;
  questionLimit = data.questionLimit;
  revelationCount = data.display.revelationCount;
  publicTimeline = data.publicTimeline;
}
