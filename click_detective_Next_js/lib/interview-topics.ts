import { suspects, type SuspectId } from './case';
/** 백엔드가 공개한 질문 주제만 원본 버튼으로 표시합니다. */
export function getInterviewTopics(speaker: SuspectId) {
  return suspects.find((p) => p.id === speaker)?.interviewTopics ?? [];
}
