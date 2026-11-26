'use client';

import { useRef, useState } from 'react';
import type { FormEvent } from 'react';
import { authRequest, withAuthLock } from '@/shared/auth/client';
import { SIGNUP_PASSWORD_HINT, isSignupPassword } from '@/shared/auth/password';
import { ApiError } from '@/shared/api/error';
import { announceAccountChange } from './session';
import { AccountFrame } from './account-frame';

/** 회원가입 또는 로그인 폼을 표시하고 공개 인증 응답을 처리한다.
 * @param props 화면 유형과 가입 완료 안내 여부.
 * @returns 인증 화면.
 */
export function AuthForm({ signup, created = false }: { signup: boolean; created?: boolean }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [fields, setFields] = useState<Record<string, string>>({});
  const submitting = useRef(false);
  /** 중복 제출을 막고 유효한 로그인 또는 가입 입력을 보낸다.
   * @param event 폼 제출 이벤트.
   * @returns 인증 처리와 안내가 끝나면 완료되는 Promise.
   */
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting.current) return;
    setError('');
    setFields({});
    if (signup && !isSignupPassword(password)) {
      setFields({ password: SIGNUP_PASSWORD_HINT });
      return;
    }
    if (signup && password !== confirmation) {
      setFields({ confirmation: '비밀번호가 일치하지 않습니다.' });
      return;
    }
    submitting.current = true;
    setBusy(true);
    try {
      const input = { email, password };
      if (signup) {
        await authRequest('signup', input);
        window.location.assign('/login?created=1');
      } else {
        await withAuthLock(() => authRequest('login', input));
        announceAccountChange();
        window.location.assign('/');
      }
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : '인증 요청에 실패했습니다.');
      if (failure instanceof ApiError) setFields(failure.fields);

      setPassword('');
      setConfirmation('');
      setBusy(false);
      submitting.current = false;
    }
  }

  if (busy) return null;

  return (
    <AccountFrame title={signup ? '회원가입' : '로그인'}>
      {created && <p role="status">가입이 완료되었습니다. 로그인하세요.</p>}
      <form className="account-form" onSubmit={submit}>
        <label htmlFor="account-email">이메일</label>
        <input
          id="account-email"
          type="email"
          name="email"
          autoComplete="username"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          aria-invalid={Boolean(fields.email)}
          aria-describedby={fields.email ? 'account-email-error' : undefined}
        />
        {fields.email && (
          <p id="account-email-error" role="alert">
            {fields.email}
          </p>
        )}
        <label htmlFor="account-password">비밀번호</label>
        <input
          id="account-password"
          name="password"
          type="password"
          autoComplete={signup ? 'new-password' : 'current-password'}
          required
          maxLength={signup ? undefined : 256}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          aria-invalid={Boolean(fields.password)}
          aria-describedby={
            fields.password
              ? 'account-password-error'
              : signup
                ? 'account-password-hint'
                : undefined
          }
        />
        {signup && !fields.password && <p id="account-password-hint">{SIGNUP_PASSWORD_HINT}</p>}
        {fields.password && (
          <p id="account-password-error" role="alert">
            {fields.password}
          </p>
        )}
        {signup && (
          <>
            <label htmlFor="account-confirmation">비밀번호 확인</label>
            <input
              id="account-confirmation"
              name="confirmation"
              type="password"
              autoComplete="new-password"
              required
              value={confirmation}
              onChange={(event) => setConfirmation(event.target.value)}
              aria-invalid={Boolean(fields.confirmation)}
              aria-describedby={fields.confirmation ? 'account-confirmation-error' : undefined}
            />
            {fields.confirmation && (
              <p id="account-confirmation-error" role="alert">
                {fields.confirmation}
              </p>
            )}
          </>
        )}
        {error && <p role="alert">{error}</p>}
        <button type="submit" className="primary">
          {signup ? '가입하기' : '로그인'}
        </button>
      </form>
      <a href={signup ? '/login' : '/signup'}>{signup ? '로그인' : '회원가입'}</a>
    </AccountFrame>
  );
}
