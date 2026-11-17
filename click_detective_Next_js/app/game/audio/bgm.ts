/** 게임 전체에서 하나만 쓰는 배경음 플레이어.
 * 브라우저 자동재생 정책 때문에 재생은 반드시 사용자 클릭 처리 안에서 시작한다.
 */
const BGM_SRC = '/assets/audio/bgm.mp3';
const STORAGE_KEY = 'click-detective-bgm';
const VOLUME = 0.35;

let audio: HTMLAudioElement | null = null;
const listeners = new Set<(playing: boolean) => void>();

/** 배경음 오디오 객체를 처음 한 번만 만든다.
 * 파라미터 없음.
 * @returns 반복 재생으로 설정한 오디오 객체.
 */
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

/** 사용자가 마지막으로 고른 켜기/끄기 상태를 저장한다.
 * @param on 켜져 있으면 true.
 * @returns 없음.
 */
function remember(on: boolean) {
  try {
    localStorage.setItem(STORAGE_KEY, on ? 'on' : 'off');
  } catch {}
}

export const bgm = {
  /** 페이지가 열리면 음원을 미리 받아 버튼을 누르는 즉시 재생되게 한다.
   * 파라미터 없음.
   * @returns 없음.
   */
  preload() {
    const a = getAudio();
    if (a.paused && a.readyState === 0) a.load();
  },
  /** 배경음이 재생 중인지 확인한다.
   * 파라미터 없음.
   * @returns 재생 중이면 true.
   */
  isPlaying: () => !!audio && !audio.paused,
  /** 「사건 시작하기」·「수사 이어하기」 클릭 때 호출해 배경음을 시작한다.
   * 파라미터 없음.
   * @returns 없음.
   */
  startFromGame() {
    if (bgm.isPlaying()) return;
    getAudio()
      .play()
      .catch(() => {});
  },
  /** 상단 BGM 버튼으로 배경음을 끄거나 켠다.
   * 파라미터 없음.
   * @returns 재생 상태 변경이 끝나면 완료되는 Promise.
   */
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
  /** 재생 상태가 바뀔 때 알림을 받는다.
   * @param fn 재생 상태를 받는 함수.
   * @returns 알림을 해제하는 함수.
   */
  subscribe(fn: (playing: boolean) => void) {
    listeners.add(fn);
    return () => {
      listeners.delete(fn);
    };
  },
};
