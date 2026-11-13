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
export type Readiness = {
  inference: number;
  findings: number;
  eligible: boolean;
};
export type Progress = {
  counts: { evidence: number; findings: number; inference: number };
  goals: { evidence: number; findings: number; inference: number };
  completed: number;
  total: number;
  percent: number;
};
export type DisplaySource = {
  ref: SourceRef;
  category: 'evidence' | 'testimony' | 'derived';
  code: string;
  title: string;
  context: string;
};
export type Presentation = {
  requiredInferenceIds: string[];
  basisLabels: Record<string, string>;
  physicalCount: number;
  physicalReadCount: number;
};
export let caseInfo: {
  id: string;
  title: string;
  englishTitle: string;
  place: string;
  number: string;
  duration: string;
  summary: string;
};
export let suspects: Person[] = [];
export let evidence: EvidenceRecord[] = [];
export let motiveOptions: { id: string; label: string }[] = [];
export let methodOptions: { id: string; label: string }[] = [];
export let questionLimit = 0;
export let revelationCount = 0;
export let publicTimeline: TimelineEntry[] = [];
export interface PublicCatalog {
  case: typeof caseInfo;
  characters: Person[];
  motiveOptions: typeof motiveOptions;
  methodOptions: typeof methodOptions;
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
/** 브라우저가 초기 카탈로그를 받은 후 원본 화면의 읽기 전용 표시 자료를 준비합니다. */
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
export type StatementNature =
  '본인 진술' | '직접 목격' | '전언' | '추측·인상' | '심문에서 인정';
export type AcquiredStatement = {
  id: string;
  code: string;
  speaker: SuspectId;
  topic: string;
  target?: SuspectId;
  title: string;
  excerpt: string;
  messageIndex: number;
  nature: StatementNature;
  sourceRefs: SourceRef[];
  time?: string;
  start?: number;
  end?: number;
  supersedes?: string[];
  source: { file: string; pages: number[]; section: string };
};
export type TimelineEntry = {
  id: string;
  time: string;
  start: number;
  end?: number;
  title: string;
  text: string;
  category: string;
  statementId?: string;
  evidenceId?: string;
  derivedId?: string;
  speaker?: SuspectId;
};

export type EvidenceId = string;
export type SuspectId = 'yoon' | 'baek' | 'kang' | 'cha' | 'seo';
export type Message = {
  suspectId: SuspectId;
  role: 'user' | 'suspect';
  text: string;
  evidenceId?: string;
  topicId?: string;
};
export type ReviewItem = {
  id: string;
  title: string;
  discovered: boolean;
  submitted?: boolean;
};
export type EvidenceAssessment = {
  submitted: {
    id: string;
    title: string;
    kind: 'evidence' | 'derived';
    contributes: boolean;
    coveredTitles: string[];
  }[];
  missing: { id: string; title: string }[];
};
export type InvestigationReview = {
  findings: ReviewItem[];
  inference: ReviewItem[];
};
export type Verdict = {
  checkDetails?: Record<string, string>;
  submittedEvidenceIds?: string[];
  evidenceAssessment?: EvidenceAssessment;
  review?: InvestigationReview;
  correct: boolean;
  score: number;
  checks: { label: string; correct: boolean }[];
  explanation: string;
};
/** kind와 id를 함께 저장한다. 증거·증언·추론의 ID를 혼동하지 않기 위한 참조다. */
export type SourceRef = {
  kind: 'evidence' | 'derived' | 'testimony';
  id: string;
};
/** sourceRefs=직접 연결, leafSources=선행 추론을 펼친 원본 근거. */
export type DerivedEvidence = {
  id: string;
  code: string;
  kind: 'derived';
  investigationPhase?: 1 | 2;
  construction?: 'base' | 'chain';
  type: string;
  title: string;
  time: string;
  summary: string;
  phase: 1 | 2;
  body: string;
  sourceRefs: SourceRef[];
  leafSources: SourceRef[];
};
export type FindingDetail = {
  title: string;
  suspectId: SuspectId;
  sourceRefs: SourceRef[];
  messageIndex: number;
};
/** 한 수사의 저장 단위. React 화면은 서버가 돌려준 이 상태를 다시 표시한다. */
export type GameState = {
  id: string;
  caseId: string;
  revision: number;
  scenarioVersion: string;
  ui: Presentation;
  progress: Progress;
  secondRoundEligibility: Readiness;
  accusationReadiness: Readiness;
  inferenceSources: DisplaySource[];
  startedAt: string;
  phase: 1 | 2;
  examined: string[];
  statements: Record<string, AcquiredStatement>;
  timeline: TimelineEntry[];
  contradictions: string[];
  findingDetails: FindingDetail[];
  derivedEvidence: Record<string, DerivedEvidence>;
  inferenceTotal: number;
  archivedInference?: Record<string, DerivedEvidence>;
  revealed: string[];
  messages: Message[];
  notes: string;
  questions: number;
  verdict: Verdict | null;
};
