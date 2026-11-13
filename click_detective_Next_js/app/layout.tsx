import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: '딸깍탐정단 — AI 추리게임',
  description:
    '증거를 조사하고, 용의자를 심문하고, 진실을 밝혀내세요. 플레이 가능한 독립 추리 게임 데모.',
};
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
