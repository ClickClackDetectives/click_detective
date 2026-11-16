'use client';

import { useEffect, useRef, useState } from 'react';
import { Play, RotateCcw, Volume2, X } from 'lucide-react';

/** 오프닝 영상 팝업과 재생 버튼을 표시한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.gameId 현재 수사의 ID.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function CaseOpening({ gameId }: { gameId: string }) {
  const video = useRef<HTMLVideoElement>(null);
  const closeButton = useRef<HTMLButtonElement>(null);
  const replayButton = useRef<HTMLButtonElement>(null);
  const [open, setOpen] = useState(false);
  const [blocked, setBlocked] = useState(false);
  const [ended, setEnded] = useState(false);

  useEffect(() => {
    const key = `detective-opening-v3:${gameId}`;
    try {
      if (localStorage.getItem(key)) return;
      localStorage.setItem(key, 'seen');
    } catch {
      // Storage-disabled browsers retain the marker for this page session.
      if (document.documentElement.dataset.openingSeen === gameId) return;
      document.documentElement.dataset.openingSeen = gameId;
    }
    setOpen(true);
  }, [gameId]);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    closeButton.current?.focus();
    let active = true;
    const player = video.current;
    player?.play().catch(() => {
      if (active) setBlocked(true);
    });
    /** 오프닝 팝업의 키보드 이동을 처리한다.
     * @param event 브라우저 이벤트.
     * @returns 없음. Escape 닫기와 Tab 초점 이동을 처리한다.
     */
    function keys(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false);
      if (event.key === 'Tab') {
        const dialog = closeButton.current?.closest('[role="dialog"]');
        const controls = dialog?.querySelectorAll<HTMLElement>(
          'button:not(:disabled), video[controls]',
        );
        if (!controls?.length) return;
        const first = controls[0],
          last = controls[controls.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    }
    document.addEventListener('keydown', keys);
    return () => {
      active = false;
      player?.pause();
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', keys);
      replayButton.current?.focus();
    };
  }, [open]);

  /** 오프닝 영상을 처음부터 재생한다.
   * 파라미터 없음.
   * @returns 영상 재생을 시도하고 차단 안내를 적용하면 완료되는 Promise.
   */
  async function play() {
    if (!video.current) return;
    video.current.currentTime = 0;
    try {
      await video.current.play();
      setBlocked(false);
      setEnded(false);
    } catch {
      setBlocked(true);
    }
  }

  return (
    <>
      <section className="opening-replay-card" aria-label="사건 오프닝">
        <div>
          <span className="eyebrow">PROLOGUE / 사건의 시작</span>
          <p>열세 번째 종 · 폭풍우가 몰아친 그날 밤</p>
        </div>
        <button
          ref={replayButton}
          type="button"
          className="opening-play"
          onClick={() => {
            setEnded(false);
            setBlocked(false);
            setOpen(true);
          }}
        >
          <Play size={17} /> 오프닝 다시 보기
        </button>
      </section>
      {open && (
        <div className="opening-modal-backdrop" onClick={() => setOpen(false)}>
          <section
            className="opening-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="opening-title"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="opening-label">
              <span id="opening-title">열세 번째 종 · PROLOGUE</span>
              <span>
                <Volume2 size={13} /> SOUND ON{' '}
                <button
                  ref={closeButton}
                  type="button"
                  aria-label="오프닝 닫기"
                  onClick={() => setOpen(false)}
                >
                  <X size={22} />
                </button>
              </span>
            </div>
            <div className="opening-screen">
              <video
                ref={video}
                src="/assets/intro/thirteenth-bell-opening-v3-quiet.mp4"
                playsInline
                autoPlay
                controls
                preload="auto"
                onPlay={() => {
                  setBlocked(false);
                  setEnded(false);
                }}
                onEnded={() => {
                  setEnded(true);
                }}
                aria-label="열세 번째 종 사건 오프닝"
              />
              {(blocked || ended) && (
                <div className="opening-overlay ended">
                  <span className="eyebrow">BLACK CLOUD MANOR</span>
                  <h2>열세 번째 종</h2>
                  <p>
                    {blocked
                      ? '소리와 함께 보려면 재생을 눌러주세요.'
                      : '이제, 당신의 수사를 시작하세요.'}
                  </p>
                  <button className="opening-play" onClick={play}>
                    {ended ? <RotateCcw size={18} /> : <Play size={18} />}
                    {ended ? '다시 재생' : '영상 재생'}
                  </button>
                  {ended && (
                    <button className="opening-continue" onClick={() => setOpen(false)}>
                      사건 브리핑 보기 →
                    </button>
                  )}
                </div>
              )}
            </div>
          </section>
        </div>
      )}
    </>
  );
}
