/** 화면이 사용하는 오류입니다. API 키나 서버 내부 스택은 포함하지 않습니다.
 * @param message 사용자에게 보여줄 안내.
 * @param status HTTP 상태 코드.
 * @param code 오류를 구분할 코드.
 * @returns ApiError 객체.
 */
export class ApiError extends Error {
  status: number;
  code: string;
  fields: Record<string, string>;
  /** 객체에서 함께 사용할 값과 초기 상태를 준비한다.
   * @param message 사용자에게 보여줄 안내.
   * @param status HTTP 상태 코드.
   * @param code 오류를 구분할 코드.
   * @param fields 입력 항목별 공개 오류.
   * @returns 없음. 객체의 초기값을 저장한다.
   */
  constructor(message: string, status: number, code: string, fields = {}) {
    super(message);
    this.status = status;
    this.code = code;
    this.fields = fields;
  }
}
