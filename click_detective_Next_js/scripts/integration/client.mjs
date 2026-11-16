import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import path from 'node:path';

/** 쿠키와 최신 상태를 보관하면서 통합 검사 요청을 보낸다.
 * @param base 테스트 서버의 기본 주소.
 * @param key 서버 간 인증에 사용할 비밀 키.
 * @param backend FastAPI 프로젝트 폴더.
 * @returns IntegrationClient 객체.
 */
export class IntegrationClient {
  /** 객체에서 함께 사용할 값과 초기 상태를 준비한다.
   * @param base 테스트 서버의 기본 주소.
   * @param key 서버 간 인증에 사용할 비밀 키.
   * @param backend FastAPI 프로젝트 폴더.
   * @returns 없음. 객체의 초기값을 저장한다.
   */
  constructor(base, key, backend) {
    this.base = base;
    this.key = key;
    this.backend = backend;
    this.cookies = '';
    this.records = [];
    this.state = null;
  }
  /** 쿠키를 유지하며 HTTP 요청을 보내고 응답과 상태 코드를 검사한다.
   * @param route 호출할 API 경로.
   * @param props 검사에 사용할 설정과 데이터.
   * @param props.method HTTP 요청 메서드.
   * @param props.body 전송할 요청 본문.
   * @param props.status HTTP 상태 코드.
   * @param props.origin 브라우저가 보낸 Origin 헤더.
   * @param props.headers 추가 요청 헤더.
   * @returns 상태 코드를 확인하고 기록한 응답 JSON.
   */
  async request(
    route,
    { method = 'GET', body, status = 200, origin = this.base, headers = {} } = {},
  ) {
    const response = await fetch(
      this.base + (route.startsWith('/') ? route : '/api/detective/' + route),
      {
        method,
        headers: {
          ...(this.cookies ? { cookie: this.cookies } : {}),
          ...(method === 'GET' ? {} : { origin, 'Content-Type': 'application/json' }),
          ...headers,
        },
        ...(body ? { body: JSON.stringify(body) } : {}),
      },
    );
    const text = await response.text();
    let output;
    try {
      output = JSON.parse(text);
    } catch {
      output = {
        bytes: Buffer.byteLength(text),
        contentType: response.headers.get('content-type'),
      };
    }
    this.records.push({
      route,
      method,
      input: body ?? null,
      expectedStatus: status,
      status: response.status,
      output,
    });
    assert.equal(response.status, status, `${method} ${route}: ${text.slice(0, 500)}`);
    const setCookies = response.headers.getSetCookie();
    if (setCookies.length) {
      assert.ok(setCookies.every((c) => /httponly/i.test(c)));
      this.cookies = setCookies.map((c) => c.split(';')[0]).join('; ');
    }
    assert.ok(!text.includes(this.key), '서버 키 노출');
    assert.ok(!text.includes('game_token'), '수사 토큰 본문 노출');
    return output;
  }
  /** UUID와 현재 저장 버전을 붙여 수사 행동을 실행한다.
   * @param route 호출할 API 경로.
   * @param fields 행동 요청에 추가할 입력값.
   * @param method HTTP 요청 메서드.
   * @returns 최신 수사 상태가 반영된 행동 응답.
   */
  async act(route, fields, method = 'POST') {
    const data = await this.request(route, {
      method,
      body: {
        request_id: randomUUID(),
        expected_revision: this.state.revision,
        ...fields,
      },
    });
    this.state = data.state;
    return data;
  }

  /** 검사에 사용할 사건 JSON을 읽는다.
   * @param name 파일·사례·화면의 이름.
   * @returns 지정한 사건 파일의 JSON 객체.
   */
  async readCase(name) {
    const text = await readFile(path.join(this.backend, 'data/case', name), 'utf8');
    return JSON.parse(text);
  }
}
