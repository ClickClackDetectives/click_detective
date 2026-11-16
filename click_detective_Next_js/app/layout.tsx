import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: '딸깍탐정단 — AI 추리게임',
  description:
    '증거를 조사하고, 용의자를 심문하고, 진실을 밝혀내세요. 플레이 가능한 독립 추리 게임 데모.',
};
/** 모든 화면에 공통 HTML과 스타일을 적용한다.
 * @param props 화면에 전달한 상태와 사용자 행동 함수.
 * @param props.children 공통 레이아웃 안에 표시할 화면.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
