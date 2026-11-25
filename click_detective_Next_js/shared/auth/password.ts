export const SIGNUP_PASSWORD_HINT =
  '비밀번호는 8~16자로 입력하고 영문, 숫자, 특수문자를 각각 포함하세요.';

/** 가입 비밀번호 길이와 필수 문자 조합을 검사한다.
 * @param password 사용자가 회원가입 화면에 입력한 비밀번호.
 * @returns 8~16자이며 영문, 숫자, ASCII 특수문자가 각각 있으면 true.
 */
export function isSignupPassword(password: string): boolean {
  const length = [...password].length;
  const hasLetter = /[A-Za-z]/.test(password);
  const hasDigit = /[0-9]/.test(password);
  const hasSpecial = /[\x21-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e]/.test(password);
  return length >= 8 && length <= 16 && hasLetter && hasDigit && hasSpecial;
}
