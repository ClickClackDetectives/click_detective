# PostgreSQL 설치와 실행

계정 로그인과 세션을 활성화하는 환경에서 PostgreSQL을 준비한다. 앱 연결과 검사용 임시 스키마에 사용하는 연결 문자열은 각각의 변수로 설정한다.

## Ubuntu에서 새로 설치하기

Ubuntu 기본 저장소의 패키지를 설치하고 서비스를 시작합니다. [PostgreSQL Ubuntu 설치 문서](https://www.postgresql.org/download/linux/ubuntu/)

```sh
sudo apt update
sudo apt install postgresql
sudo systemctl enable --now postgresql
pg_isready -h 127.0.0.1 -p 5432
```

처음에는 앱 전용 역할과 데이터베이스를 만듭니다. `--pwprompt`에 입력한 비밀번호는 FastAPI 연결 설정에도 사용합니다. 앱은 시작할 때 이 데이터베이스에 인증 테이블과 인덱스를 준비합니다.

```sh
sudo -u postgres createuser --pwprompt click_detective_app
sudo -u postgres createdb --owner=click_detective_app click_detective
psql -h 127.0.0.1 -p 5432 -U click_detective_app -d click_detective -W -c 'SELECT current_database();'
```

FastAPI의 `.env`에 아래 연결 값을 지정합니다. 비밀번호에 `@`, `:`, `/` 등 URI 예약 문자가 들어가면 퍼센트 인코딩합니다.

```dotenv
CLICK_POSTGRES_DSN=postgresql://click_detective_app:YOUR_PASSWORD@127.0.0.1:5432/click_detective
```

서비스 상태 확인에는 `sudo systemctl status postgresql`, 시작에는 `sudo systemctl start postgresql`, 종료에는 `sudo systemctl stop postgresql`을 사용합니다. 개별 클러스터 상태는 `pg_lsclusters`에서 확인합니다.

## 기존 작업공간의 사용자 설치 실행하기

이 작업공간의 PostgreSQL 18은 `click_detective_FastAPI/.data/local-db` 아래에 설치되어 있습니다. Unix 소켓의 포트 번호는 `15432`이며, 설치한 OS 계정이 peer 인증으로 접속합니다. FastAPI 디렉터리에서 실행합니다.

```sh
db_dir="$PWD/.data/local-db"
pg_dir="$db_dir/postgres"
export LD_LIBRARY_PATH="$pg_dir/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
install -d -m 700 /tmp/click-detective-db/socket
"$pg_dir/usr/lib/postgresql/18/bin/pg_ctl" -D "$db_dir/pg-data" \
  -l "$db_dir/postgres.log" -o "-c listen_addresses='' -k /tmp/click-detective-db/socket -p 15432" start
"$pg_dir/usr/lib/postgresql/18/bin/psql" -h /tmp/click-detective-db/socket \
  -p 15432 -d click_detective -c 'SELECT current_database();'
```

같은 셸에서 상태를 확인할 때는 `"$pg_dir/usr/lib/postgresql/18/bin/pg_ctl" -D "$db_dir/pg-data" status`를 실행합니다. 종료할 때는 마지막 인자를 `stop`으로 바꿉니다. 사용자 설치의 FastAPI 연결 설정은 [계정과 수사 저장소](../시작하기/05_계정과_수사_저장소.md)에서 확인합니다.
