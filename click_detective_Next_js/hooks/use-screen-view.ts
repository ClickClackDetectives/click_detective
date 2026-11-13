'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/client-api';
import type {
  GameState,
  EvidenceRecord,
  Message,
  AcquiredStatement,
  DisplaySource,
} from '@/lib/case';
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
/** 원본 필터 UI는 유지하고 검색·분류 결과를 FastAPI에서 받아 표시합니다. */
export function useScreenView<T>(
  screen: string,
  state: GameState,
  query: Record<string, string>,
  initial: T,
) {
  const [result, setResult] = useState<T>(initial),
    [error, setError] = useState('');
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
