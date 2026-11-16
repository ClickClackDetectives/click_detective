/** 화면의 기존 행동 이름을 FastAPI 계약으로 바꿉니다. 규칙을 판정하지 않습니다.
 * @param action 실행할 수사 행동 이름.
 * @param input 화면에서 받은 행동 입력.
 * @returns 백엔드 행동 경로와 요청 필드.
 */
export function mapGameCommand(action: string, input: Record<string, unknown>) {
  switch (action) {
    case 'examine':
      return {
        path: 'examinations',
        fields: { evidence_id: input.evidenceId },
      };
    case 'interrogate':
      return {
        path: 'interrogations',
        fields: {
          suspect_id: input.suspectId,
          question: input.question,
          ...(input.topicId ? { topic_id: input.topicId } : {}),
          ...(input.evidenceId ? { material_id: input.evidenceId } : {}),
        },
      };
    case 'connect-evidence':
      return { path: 'inferences', fields: { sources: input.sources } };
    case 'advance':
      return { path: 'phase-transitions', fields: { target_phase: 2 } };
    case 'notes':
      return { path: 'notes', method: 'PUT', fields: { text: input.text } };
    case 'accuse':
      return {
        path: 'accusations',
        fields: {
          suspect_id: input.suspectId,
          motive: input.motive,
          method: input.method,
          evidence_ids: input.evidenceIds,
        },
      };
    default:
      throw new Error('지원하지 않는 수사 행동입니다.');
  }
}
