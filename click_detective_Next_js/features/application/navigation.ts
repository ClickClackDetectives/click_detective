import {
  LayoutDashboard,
  FolderOpen,
  MessageSquare,
  Clock3,
  StickyNote,
  Scale,
  Fingerprint,
  Link2,
} from 'lucide-react';
export type View =
  | 'home'
  | 'cases'
  | 'briefing'
  | 'evidence'
  | 'testimonies'
  | 'interrogate'
  | 'timeline'
  | 'notes'
  | 'accuse'
  | 'results'
  | 'findings'
  | 'inference';
export const tabs = [
  { id: 'briefing', label: '사건 브리핑', icon: LayoutDashboard },
  { id: 'evidence', label: '증거 보관실', icon: FolderOpen },
  { id: 'testimonies', label: '증언 기록', icon: MessageSquare },
  { id: 'interrogate', label: '용의자 심문', icon: MessageSquare },
  { id: 'findings', label: '발견한 쟁점', icon: Fingerprint },
  { id: 'inference', label: '추론 증거', icon: Link2 },
  { id: 'timeline', label: '사건 타임라인', icon: Clock3 },
  { id: 'notes', label: '수사 노트', icon: StickyNote },
  { id: 'accuse', label: '최종 고발', icon: Scale },
] as const;
