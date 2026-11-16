import type { SuspectId, TimelineEntry } from '../investigation/types';

/** 사건 소개와 화면 선택지의 자료형이다. */
export type CaseInfo = {
  id: string;
  title: string;
  englishTitle: string;
  place: string;
  number: string;
  duration: string;
  summary: string;
};
export type Choice = { id: string; label: string };
/** 원본 화면이 사용하는 표시용 타입. 사건 값과 집계는 FastAPI 응답으로만 채웁니다. */
export type EvidenceRecord = {
  id: string;
  code: string;
  type: string;
  title: string;
  time: string;
  phase: 1 | 2;
  summary: string;
  body: string;
  archiveKind?: string;
};

export type Person = {
  id: SuspectId;
  name: string;
  en: string;
  age: number;
  role: string;
  portrait: string;
  initials: string;
  color: string;
  statement: string;
  bio: string;
  suggestions: string[];
  interviewTopics: { id: string; label: string; question: string }[];
};

export interface PublicCatalog {
  case: CaseInfo;
  characters: Person[];
  motiveOptions: Choice[];
  methodOptions: Choice[];
  questionLimit: number;
  publicTimeline: TimelineEntry[];
  application: { cases: import('./case-library').LibraryCase[] };
  display: {
    evidence: EvidenceRecord[];
    revelationCount: number;
    secondRoundRequirements: { inference: number; findings: number };
    accusationMinimum: number;
  };
  caseId: string;
  scenarioVersion: string;
}
