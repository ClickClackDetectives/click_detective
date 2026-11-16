'use client';
import { useEffect, useState } from 'react';
import { api } from '@/shared/api/client';
import type {
  GameState,
  Message,
  AcquiredStatement,
  DisplaySource,
} from '@/app/game/investigation/types';
import type { EvidenceRecord } from '@/app/game/catalog/types';
export type EvidenceView = {
  available: EvidenceRecord[];
  places: string[];
  groups: { name: string; records: EvidenceRecord[] }[];
  readCount: number;
};
export type TestimonyView = {
  visible: {
    id: string;
    name: string;
    initial: string | null;
    records: EvidenceRecord[];
    acquired: AcquiredStatement[];
    pairs: {
      question: Message & { index: number };
      answer: (Message & { index: number }) | null;
    }[];
  }[];
};
export type InferenceView = { visible: DisplaySource[] };
/** 원본 필터 UI는 유지하고 검색·분류 결과를 FastAPI에서 받아 표시합니다.
 * @param screen 검색할 화면 이름.
 * @param state 서버에서 확인한 현재 수사 상태.
 * @param query 화면에서 선택한 검색 조건.
 * @param initial 첫 응답 전 사용할 기본값.
 * @returns 서버의 화면 조회 결과와 오류 안내.
 */
export function useScreenView<T>(
  screen: string,
  state: GameState,
  query: Record<string, string>,
  initial: T,
) {
  const [result, setResult] = useState<T>(initial);
  const [error, setError] = useState('');
  const params = new URLSearchParams(query).toString();
  useEffect(() => {
    let alive = true;
    api<T>('views/' + screen + '?' + params)
      .then((data) => {
        if (alive) {
          setResult(data);
          setError('');
        }
      })
      .catch((e) => {
        if (alive) setError(e.message);
      });
    return () => {
      alive = false;
    };
  }, [screen, params, state.id, state.revision]);
  return { ...result, error };
}
