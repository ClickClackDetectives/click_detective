import { api, assetUrl } from '../../../shared/api/client.ts';
import type { GameState } from './types';
import { evidenceIllustrations } from '../materials/illustrations.ts';
import type { InvestigationDocument } from '../materials/document-types';
/** 원본 팝업의 문서 형태를 서버 상세 응답에서 만듭니다. 본문은 미리 번들에 넣지 않습니다.
 * @param id 자료 또는 수사 식별자.
 * @param state 서버에서 확인한 현재 수사 상태.
 * @returns 화면에 표시할 원본·진술·추론 문서.
 */
export async function requestDocument(
  id: string,
  state: GameState,
): Promise<InvestigationDocument> {
  let kind = 'evidence';
  if (state.statements[id]) kind = 'testimony';
  if (state.derivedEvidence[id]) kind = 'derived';
  const data = await api<
    InvestigationDocument & {
      excerpt?: string;
      illustration?: string;
      nature?: string;
      time?: string;
      source?: { file: string; pages: number[]; section: string };
      speaker?: string;
      messageIndex?: number;
    }
  >('materials/' + encodeURIComponent(kind + ':' + id));
  if (data.illustration) evidenceIllustrations[id] = assetUrl(data.illustration);
  if (kind === 'testimony') {
    const { suspects } = await import('../catalog/catalog.ts');
    const speaker = suspects.find((p) => p.id === data.speaker)?.name;
    const heading = data.nature + (data.time ? ' · ' + data.time : '');
    const answer = state.messages[data.messageIndex ?? -1]?.text ?? data.excerpt;
    const source = data.source
      ? `출처: ${data.source.file} · ${data.source.pages.join(', ')}쪽 · ${data.source.section}`
      : '';
    return {
      ...data,
      type: data.nature ?? '증언',
      body: [speaker, heading, answer, source].filter(Boolean).join('\n\n'),
    };
  }
  return data;
}
