import { suspects } from '../catalog/catalog';
import type { SuspectId } from '../investigation/types';
/** 백엔드가 공개한 질문 주제만 원본 버튼으로 표시합니다.
 * @param speaker 질문 주제를 조회할 인물 ID.
 * @returns 선택한 인물의 공개 질문 주제 목록. 인물이 없으면 빈 배열.
 */
export function getInterviewTopics(speaker: SuspectId) {
  return suspects.find((p) => p.id === speaker)?.interviewTopics ?? [];
}
