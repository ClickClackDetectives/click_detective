import { AccountGate } from '@/components/auth/account-gate';
import { isInvestigationId } from '@/shared/auth/contract';
import { OriginalAppLoader } from '@/components/application/original-app-loader';
import { notFound } from 'next/navigation';

/** 선택한 계정 수사나 새 수사를 기존 수사 화면에서 연다.
 * @param props 계정 수사를 결정할 검색 파라미터.
 * @returns 로그인 계정에서 열 수 있는 수사 화면.
 */
export default async function AccountGamePage({
  searchParams,
}: {
  searchParams: Promise<{ investigation?: string }>;
}) {
  const { investigation } = await searchParams;
  if (typeof investigation !== 'string') notFound();
  if (investigation !== 'new' && !isInvestigationId(investigation)) notFound();
  return (
    <AccountGate destination={'/game?investigation=' + investigation}>
      <OriginalAppLoader />
    </AccountGate>
  );
}
