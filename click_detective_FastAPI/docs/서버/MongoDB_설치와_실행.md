# MongoDB 설치와 실행

FastAPI 수사 저장소는 MongoDB 트랜잭션을 사용하므로 replica set 연결이 필요하다. 시스템 설치와 작업공간의 사용자 설치 중 해당하는 절차를 따른다.

## Ubuntu에서 새로 설치하기

아래 명령은 **Ubuntu 26.04 LTS**에서 MongoDB Community 9.0을 설치합니다. 다른 Ubuntu 버전에서는 공식 안내에서 배포판에 맞는 저장소를 선택합니다. [MongoDB Ubuntu 설치 문서](https://www.mongodb.com/docs/manual/administration/install-community-linux/?linux-distro=ubuntu&linux-method=pkg) · [지원 플랫폼](https://www.mongodb.com/docs/community-platform-support/)

```sh
sudo apt update
sudo apt install gnupg curl
curl -fsSL https://pgp.mongodb.com/server-9.asc |
  sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-9.gpg
printf '%s\n' 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-9.gpg ] https://repo.mongodb.org/apt/ubuntu resolute/mongodb-org/9.0 multiverse' |
  sudo tee /etc/apt/sources.list.d/mongodb-org-9.0.list
sudo apt update
sudo apt install mongodb-org
```

### 인증과 replica set 준비

새 설치에서 아래 명령을 한 번 실행해 내부 인증 키를 만듭니다. 기존 replica set을 운영 중이라면 해당 환경에서 사용 중인 키와 설정을 사용합니다. [키 파일로 replica set 배포](https://www.mongodb.com/docs/manual/tutorial/deploy-replica-set-with-keyfile-access-control/)

```sh
openssl rand -base64 72 | sudo tee /etc/mongodb-keyfile >/dev/null
sudo chown mongodb:mongodb /etc/mongodb-keyfile
sudo chmod 400 /etc/mongodb-keyfile
sudoedit /etc/mongod.conf
```

`/etc/mongod.conf`의 해당 항목을 아래와 같이 설정합니다. 같은 최상위 키가 이미 있으면 그 안의 값을 수정합니다.

```yaml
net:
  port: 27017
  bindIp: 127.0.0.1
replication:
  replSetName: click_local
security:
  keyFile: /etc/mongodb-keyfile
```

```sh
sudo systemctl enable mongod
sudo systemctl restart mongod
mongosh --host 127.0.0.1 --port 27017
```

MongoDB 사용자 계정이 없는 새 설치라면 `mongosh`에서 한 번만 다음 명령으로 초기화합니다.

```javascript
rs.initiate({
  _id: "click_local",
  members: [{ _id: 0, host: "localhost:27017" }]
})
db.hello().isWritablePrimary
```

`db.hello().isWritablePrimary`가 `true`가 된 뒤 첫 관리자 계정을 만들고 셸을 종료합니다. [첫 사용자 생성과 localhost 예외](https://www.mongodb.com/docs/manual/core/localhost-exception/)

```javascript
db.getSiblingDB("admin").createUser({
  user: "click_admin",
  pwd: passwordPrompt(),
  roles: [{ role: "userAdminAnyDatabase", db: "admin" }]
})
exit
```

관리자로 다시 접속해 수사 데이터베이스에 앱 전용 계정을 만듭니다.

```sh
mongosh --host 127.0.0.1 --port 27017 --authenticationDatabase admin -u click_admin -p
```

```javascript
db.getSiblingDB("click_detective").createUser({
  user: "click_detective_app",
  pwd: passwordPrompt(),
  roles: [{ role: "readWrite", db: "click_detective" }]
})
exit
```

접속과 primary 상태를 확인합니다.

```sh
mongosh 'mongodb://localhost:27017/click_detective?replicaSet=click_local' \
  -u click_detective_app -p --eval 'db.hello().isWritablePrimary'
```

FastAPI의 `.env`에 앱 계정 연결 정보를 설정합니다. 비밀번호의 URI 예약 문자는 퍼센트 인코딩합니다.

```dotenv
CLICK_MONGO_URI=mongodb://click_detective_app:YOUR_PASSWORD@localhost:27017/?authSource=click_detective&replicaSet=click_local
CLICK_MONGO_DATABASE=click_detective
```

공식 APT 패키지의 서비스 이름은 `mongod.service`입니다. 상태 확인에는 `sudo systemctl status mongod`, 시작에는 `sudo systemctl start mongod`, 종료에는 `sudo systemctl stop mongod`를 사용합니다.

## 기존 작업공간의 사용자 설치 실행하기

이 작업공간에서는 `.data/local-db/mongo/bin/mongod`를 직접 실행합니다. FastAPI 디렉터리에서 기존 데이터와 키 파일로 시작합니다.

```sh
db_dir="$PWD/.data/local-db"
"$db_dir/mongo/bin/mongod" --dbpath "$db_dir/mongo-data" --logpath "$db_dir/mongo.log" \
  --pidfilepath "$db_dir/mongo.pid" --port 27018 --bind_ip 127.0.0.1 \
  --replSet click_local --keyFile "$db_dir/mongo-key" --fork
```

이 설치의 프로세스는 `ps -p "$(cat .data/local-db/mongo.pid)" -o pid,comm`으로 확인합니다. 기존 연결은 `127.0.0.1:27018`을 사용합니다. FastAPI 연결과 실행은 [계정과 수사 저장소](../시작하기/05_계정과_수사_저장소.md)에서 확인합니다.
