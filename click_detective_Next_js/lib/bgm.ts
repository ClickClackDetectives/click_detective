/** 게임 전체에서 하나만 쓰는 배경음 플레이어.
 *  브라우저 자동재생 정책 때문에 반드시 사용자 클릭 처리 안에서 play()를 불러야 합니다. */
const BGM_SRC = '/assets/audio/bgm.mp3';
const STORAGE_KEY = 'click-detective-bgm';
const VOLUME = 0.35;

let audio: HTMLAudioElement | null = null;
const listeners = new Set<(playing: boolean) => void>();

function getAudio() {
  if (!audio) {
    audio = new Audio(BGM_SRC);
    audio.loop = true;
    audio.preload = 'auto';
    audio.volume = VOLUME;
    audio.addEventListener('play', () => listeners.forEach((fn) => fn(true)));
    audio.addEventListener('pause', () => listeners.forEach((fn) => fn(false)));
  }
  return audio;
}

function remember(on: boolean) {
  try {
    localStorage.setItem(STORAGE_KEY, on ? 'on' : 'off');
  } catch {}
}

export const bgm = {
  /** 페이지가 열리면 미리 받아둬서 버튼을 누르는 즉시 재생되게 한다. */
  preload() {
    const a = getAudio();
    if (a.paused && a.readyState === 0) a.load();
  },
  isPlaying: () => !!audio && !audio.paused,
  /** 「사건 시작하기」·「수사 이어하기」 클릭 때 호출. 항상 재생을 시작한다. */
  startFromGame() {
    if (bgm.isPlaying()) return;
    getAudio().play().catch(() => {});
  },
  async toggle() {
    if (bgm.isPlaying()) {
      getAudio().pause();
      remember(false);
    } else {
      try {
        await getAudio().play();
        remember(true);
      } catch {}
    }
  },
  subscribe(fn: (playing: boolean) => void) {
    listeners.add(fn);
    return () => {
      listeners.delete(fn);
    };
  },
};
