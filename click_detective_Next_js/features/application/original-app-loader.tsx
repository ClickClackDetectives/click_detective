'use client';
import { useEffect, useState } from 'react';
import CaseApp from './case-app';
import { api, assetUrl } from '@/shared/api/client';
import { installCatalog } from '@/features/catalog/catalog';
import type { PublicCatalog } from '@/features/catalog/types';
import { installLibrary } from '@/features/catalog/case-library';
import { installStage } from '@/features/investigation/stage';
import { installAccusation } from '@/features/accusation/requirements';
/** 사건 자료를 서버에서 준비한 다음 원본 UI를 그대로 실행합니다.
 * 파라미터 없음.
 * @returns 표시할 React 화면. 표시할 내용이 없으면 null.
 */
export function OriginalAppLoader() {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    let alive = true;
    api<PublicCatalog>('catalog')
      .then((data) => {
        if (!alive) return;
        data.characters = data.characters.map((c) => ({
          ...c,
          portrait: assetUrl(c.portrait),
        }));
        installCatalog(data);
        installLibrary(data.application.cases);
        installStage(data.display.secondRoundRequirements);
        installAccusation(data.display.accusationMinimum);
        setReady(true);
      })
      .catch((e) => {
        if (alive) setError(e.message);
      });
    return () => {
      alive = false;
    };
  }, [attempt]);
  if (ready) return <CaseApp />;
  return (
    <div className="app">
      <main className="desk">
        <p role={error ? 'alert' : 'status'}>{error || '사건 기록을 불러오고 있습니다.'}</p>
        {error && (
          <button
            className="primary"
            onClick={() => {
              setError('');
              setAttempt((x) => x + 1);
            }}
          >
            다시 연결
          </button>
        )}
      </main>
    </div>
  );
}
