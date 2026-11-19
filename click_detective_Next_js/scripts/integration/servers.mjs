import { spawn } from 'node:child_process';
import { createWriteStream } from 'node:fs';

/** 검사에서 시작한 서버만 관리하고 종료한다.
 * @param logPath 테스트 서버 로그 파일.
 * @returns TestServers 객체.
 */
export class TestServers {
  /** 객체에서 함께 사용할 값과 초기 상태를 준비한다.
   * @param logPath 테스트 서버 로그 파일.
   * @returns 없음. 객체의 초기값을 저장한다.
   */
  constructor(logPath) {
    this.log = createWriteStream(logPath);
    this.children = [];
    this.failure = null;
  }
  /** 검사에 필요한 서버 프로세스를 시작한다.
   * @param command 실행할 프로그램의 명령 또는 경로.
   * @param args 실행할 명령행 인수.
   * @param cwd 프로세스의 작업 폴더.
   * @param extra 테스트 서버에 추가할 환경변수.
   * @returns 시작한 자식 프로세스.
   */
  start(command, args, cwd, extra) {
    const child = spawn(command, args, {
      cwd,
      env: { ...process.env, ...extra },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    child.stdout.pipe(this.log, { end: false });
    child.stderr.pipe(this.log, { end: false });
    this.children.push(child);
    child.on('error', (error) => {
      this.failure = error;
    });
    return child;
  }
  /** 서버가 응답할 때까지 기다린다.
   * @param url 요청할 서버 주소.
   * @returns 서버가 준비되면 완료되는 Promise.
   */
  async ready(url) {
    for (let attempt = 0; attempt < 120; attempt++) {
      if (this.failure) throw this.failure;
      for (const child of this.children) {
        if (child.exitCode !== null)
          throw new Error('검사 서버가 종료되었습니다. 로그를 확인하세요.');
      }
      try {
        if ((await fetch(url)).ok) return;
      } catch {}
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
    throw new Error('서버 시작 대기 실패: ' + url);
  }
  /** 검사에서 시작한 프로세스를 종료한다.
   * 파라미터 없음.
   * @returns 모든 검사 프로세스 종료 후 완료되는 Promise.
   */
  async close() {
    for (const child of this.children.reverse()) {
      if (!child.pid || child.exitCode !== null || child.signalCode !== null) continue;
      const exited = new Promise((resolve) => child.once('exit', resolve));
      child.kill('SIGTERM');
      let timer;
      await Promise.race([
        exited,
        new Promise((resolve) => {
          timer = setTimeout(resolve, 3000);
        }),
      ]);
      clearTimeout(timer);
      if (child.exitCode === null && child.signalCode === null) {
        child.kill('SIGKILL');
        await exited;
      }
    }
    this.log.end();
  }
}
