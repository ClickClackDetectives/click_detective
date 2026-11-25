import { execFile } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { promisify } from 'node:util';

const execute = promisify(execFile);

const manageDatabases = `
import os
import sys
import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo

dsn = os.environ["CLICK_TEST_POSTGRES_DSN"]
name, action = sys.argv[1:]
with psycopg.connect(dsn, autocommit=True) as db:
    if action == "create":
        db.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(name)))
        print(make_conninfo(dsn, options="-c search_path=" + name))
    else:
        db.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(name)))
if action == "drop":
    from pymongo import MongoClient
    with MongoClient(os.environ["CLICK_TEST_MONGO_URI"]) as mongo:
        database = mongo[name]
        for collection in database.list_collection_names():
            database.drop_collection(collection)
`;

/** 계정 통합 검사에 사용할 고유한 PostgreSQL 스키마와 MongoDB 이름을 준비한다.
 * @param python FastAPI 프로젝트 Python 실행 파일.
 * @param backend FastAPI 프로젝트 경로.
 * @returns 검사 서버용 환경과 종료 후 정리 함수.
 */
export async function prepareAccountDatabases(python, backend) {
  const postgres = process.env.CLICK_TEST_POSTGRES_DSN;
  const mongo = process.env.CLICK_TEST_MONGO_URI;
  if (!postgres || !mongo) throw new Error('계정 통합 검사 DB 주소 두 개를 모두 설정하세요.');
  const name = 'click_fixture_' + randomUUID().replaceAll('-', '');
  /** 이 검사에서 만든 임시 이름으로만 DB 초기화 또는 정리를 실행한다.
   * @param action 스키마를 만드는 create 또는 임시 데이터 삭제를 뜻하는 drop.
   * @returns 비밀 값을 로그에 기록하지 않고 반환한 Python 프로세스의 출력.
   */
  async function manage(action) {
    try {
      const { stdout } = await execute(python, ['-c', manageDatabases, name, action], {
        cwd: backend,
        timeout: 20000,
      });
      return stdout.trim();
    } catch {
      throw new Error(
        '계정 통합 검사의 임시 DB ' + (action === 'create' ? '생성' : '정리') + ' 실패',
      );
    }
  }
  const dsn = await manage('create');
  return {
    env: {
      CLICK_POSTGRES_DSN: dsn,
      CLICK_MONGO_URI: mongo,
      CLICK_MONGO_DATABASE: name,
      CLICK_AUTH_JWT_SECRET: randomUUID() + randomUUID(),
    },
    close: () => manage('drop'),
  };
}
