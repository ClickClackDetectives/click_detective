import type { ReactNode } from 'react';
import './account.css';

/** 게임과 같은 색상으로 계정 화면의 제목과 본문을 표시한다.
 * @param props 계정 화면 제목과 내용.
 * @returns 계정 화면의 공통 구조.
 */
export function AccountFrame({ title, children }: { title: string; children: ReactNode }) {
  return (
    <main className="account-frame">
      <a href="/">딸깍탐정단</a>
      <h1>{title}</h1>
      {children}
    </main>
  );
}
