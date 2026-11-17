'use client';

import { useEffect, useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

import { bgm } from '@/lib/bgm';

/** 배경음 끄기/켜기 버튼. 재생은 「사건 시작하기」를 누를 때 자동으로 시작됩니다. */
export function BgmToggle() {
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    bgm.preload();
    setPlaying(bgm.isPlaying());
    return bgm.subscribe(setPlaying);
  }, []);

  return (
    <button
      className="outline small"
      onClick={(event) => {
        event.stopPropagation();
        void bgm.toggle();
      }}
      aria-pressed={playing}
      aria-label={playing ? '배경음 끄기' : '배경음 켜기'}
      title={playing ? '배경음 끄기' : '배경음 켜기'}
    >
      {playing ? <Volume2 size={15} /> : <VolumeX size={15} />} BGM
    </button>
  );
}
