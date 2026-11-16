import type { AcquiredStatement } from '../investigation/types';

/** 선택한 증언 분류에 해당하는지 확인한다.
 * @param item 확인할 자료 또는 진술.
 * @param section 선택한 증언 분류.
 * @returns 진술이 선택한 분류에 속하면 true.
 */
export function matchesSection(item: AcquiredStatement, section: string) {
  if (section === 'all') return true;
  if (section === 'relations') return item.topic.startsWith('about-');
  if (section === 'admission') return item.nature === '심문에서 인정';
  if (section === 'movement') {
    return item.topic === 'movement' && item.nature !== '심문에서 인정';
  }
  return false;
}
