# app/repository.py 상세 설명

[문서 목차](../../README.md) · [파일별 목차](../README.md) · [현재 소스](../../../app/repository.py)

## 역할과 읽는 순서

SQLite 수사 저장·권한·요청 예약·원자적 확정. 모델 실행 동안 DB 잠금을 잡지 않는다.

SQLite에 수사·게임 토큰 검증 정보·작업 예약·중복 응답을 저장합니다. 바인딩된 SQL 인자를 사용하고 모델 실행 중 긴 DB 트랜잭션을 유지하지 않습니다.

작성 기준: 2026-11-13 현재 소스. 아래 발췌는 실제 코드에서 가져왔으며 실행 결과나 GPU 측정 로그가 아닙니다.

## digest

[원본 17번째 줄](../../../app/repository.py#L17)

JSON 내용을 정규화해 같은 요청인지 비교한다. 값은 SQL에 바인딩한다.

### 입력과 처리

```python
def digest(value) -> str:
```

### 실제 코드

````python
def digest(value) -> str:
    """JSON 내용을 정규화해 같은 요청인지 비교한다. 값은 SQL에 바인딩한다."""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
````

## Repository

[원본 22번째 줄](../../../app/repository.py#L22)

전체 수사 상태와 완료 요청을 저장한다. 모델 프롬프트·원본 검증 출력은 저장하지 않는다.

## Repository.__init__

[원본 25번째 줄](../../../app/repository.py#L25)

게임 DB를 준비한다. 기존 기록은 삭제하지 않는다.

### 입력과 처리

```python
def __init__(self, path: Path):
```

### 실제 코드

````python
def __init__(self, path: Path):
        """게임 DB를 준비한다. 기존 기록은 삭제하지 않는다."""
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS games (id TEXT PRIMARY KEY, token_hash TEXT NOT NULL, revision INTEGER NOT NULL, state TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS operations (id TEXT PRIMARY KEY, game_id TEXT NOT NULL, digest TEXT NOT NULL, status TEXT NOT NULL, nonce TEXT, lease_until REAL, response TEXT)")
````

## Repository.transaction

[원본 34번째 줄](../../../app/repository.py#L34)

짧은 쓰기 트랜잭션을 제공한다. 실패 시 롤백하고 연결을 항상 닫는다.

### 입력과 처리

```python
def transaction(self):
```

### 실제 코드

````python
def transaction(self):
        """짧은 쓰기 트랜잭션을 제공한다. 실패 시 롤백하고 연결을 항상 닫는다."""
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()
````

## Repository._game

[원본 48번째 줄](../../../app/repository.py#L48)

수사별 비밀 토큰을 검사한다. 다른 수사의 존재도 응답으로 노출하지 않는다.

### 입력과 처리

```python
def _game(self, db, game_id, token):
```

주요 분기 조건은 `row is None or not hmac.compare_digest(row['token_hash'], hashed)`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def _game(self, db, game_id, token):
        """수사별 비밀 토큰을 검사한다. 다른 수사의 존재도 응답으로 노출하지 않는다."""
        row = db.execute("SELECT * FROM games WHERE id=?", (game_id,)).fetchone()
        hashed = hashlib.sha256(token.encode()).hexdigest()
        if row is None or not hmac.compare_digest(row["token_hash"], hashed):
            raise HTTPException(404, "수사를 찾을 수 없습니다.")
        return json.loads(row["state"])
````

## Repository.get

[원본 56번째 줄](../../../app/repository.py#L56)

저장된 수사를 복원한다. 조회만으로 게임 상태를 바꾸지 않는다.

### 입력과 처리

```python
def get(self, game_id, token):
```

### 실제 코드

````python
def get(self, game_id, token):
        """저장된 수사를 복원한다. 조회만으로 게임 상태를 바꾸지 않는다."""
        with self.transaction() as db:
            return self._game(db, game_id, token)
````

## Repository.create

[원본 61번째 줄](../../../app/repository.py#L61)

초기 수사와 재전송 응답을 같은 트랜잭션에서 저장한다.

### 입력과 처리

```python
def create(self, request, factory, present):
```

주요 분기 조건은 `previous`, `previous['digest'] != body_hash`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def create(self, request, factory, present):
        """초기 수사와 재전송 응답을 같은 트랜잭션에서 저장한다."""
        key = str(request.request_id)
        body_hash = digest({"action": "create", "body": request.model_dump(mode="json")})
        with self.transaction() as db:
            previous = db.execute("SELECT * FROM operations WHERE id=?", (key,)).fetchone()
            if previous:
                if previous["digest"] != body_hash:
                    raise HTTPException(409, "같은 요청 UUID의 내용이 다릅니다.")
                return json.loads(previous["response"])
            game_id = str(uuid4())
            token = secrets.token_urlsafe(32)
            state = factory(game_id)
            result = {"game_id": game_id, "game_token": token, "state": present(state)}
            db.execute("INSERT INTO games VALUES (?,?,?,?)", (game_id, hashlib.sha256(token.encode()).hexdigest(), 0, json.dumps(state, ensure_ascii=False)))
            db.execute("INSERT INTO operations VALUES (?,?,?,'complete',NULL,NULL,?)", (key, game_id, body_hash, json.dumps(result, ensure_ascii=False)))
            return result
````

## Repository.reserve

[원본 79번째 줄](../../../app/repository.py#L79)

실행권을 예약하고 상태 사본을 반환한다. 완료 재전송은 revision 검사보다 먼저 처리한다.

### 입력과 처리

```python
def reserve(self, game_id, token, command, action, lease_seconds):
```

주요 분기 조건은 `operation`, `state['revision'] != command.expected_revision`, `operation['digest'] != body_hash`, `operation['status'] == 'complete'`, `operation['status'] == 'pending' and operation['lease_until'] > time.time()`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def reserve(self, game_id, token, command, action, lease_seconds):
        """실행권을 예약하고 상태 사본을 반환한다. 완료 재전송은 revision 검사보다 먼저 처리한다."""
        key = str(command.request_id)
        body_hash = digest({"game_id": game_id, "action": action, "body": command.model_dump(mode="json")})
        with self.transaction() as db:
            state = self._game(db, game_id, token)
            operation = db.execute("SELECT * FROM operations WHERE id=?", (key,)).fetchone()
            if operation:
                if operation["digest"] != body_hash:
                    raise HTTPException(409, "같은 요청 UUID의 내용이 다릅니다.")
                if operation["status"] == "complete":
                    return {"cached": json.loads(operation["response"])}
                if operation["status"] == "pending" and operation["lease_until"] > time.time():
                    raise HTTPException(409, "operation_in_progress")
            if state["revision"] != command.expected_revision:
                raise HTTPException(409, "state_revision_conflict")
            nonce = str(uuid4())
            db.execute("INSERT INTO operations VALUES (?,?,?,'pending',?,?,NULL) ON CONFLICT(id) DO UPDATE SET status='pending',nonce=excluded.nonce,lease_until=excluded.lease_until",
                       (key, game_id, body_hash, nonce, time.time() + lease_seconds))
            return {"state": deepcopy(state), "nonce": nonce, "revision": state["revision"]}
````

## Repository.commit

[원본 100번째 줄](../../../app/repository.py#L100)

예약 소유권과 최신 revision을 다시 확인하고 결과·상태를 한 번 확정한다.

### 입력과 처리

```python
def commit(self, game_id, command, reservation, state, result, present):
```

주요 분기 조건은 `operation is None or operation['nonce'] != reservation['nonce'] or operation['status'] != 'pending'`, `row['revision'] != reservation['revision']`, `state != previous`입니다. 참인 경우의 처리와 거짓인 경우의 처리를 아래 코드에서 확인하세요.

### 실제 코드

````python
def commit(self, game_id, command, reservation, state, result, present):
        """예약 소유권과 최신 revision을 다시 확인하고 결과·상태를 한 번 확정한다."""
        key = str(command.request_id)
        with self.transaction() as db:
            operation = db.execute("SELECT * FROM operations WHERE id=?", (key,)).fetchone()
            row = db.execute("SELECT revision,state FROM games WHERE id=?", (game_id,)).fetchone()
            if operation is None or operation["nonce"] != reservation["nonce"] or operation["status"] != "pending":
                raise HTTPException(409, "operation_reservation_conflict")
            if row["revision"] != reservation["revision"]:
                raise HTTPException(409, "state_changed_during_generation")
            previous = json.loads(row["state"])
            if state != previous:
                state["revision"] = previous["revision"] + 1
                db.execute("UPDATE games SET state=?,revision=? WHERE id=?", (json.dumps(state, ensure_ascii=False), state["revision"], game_id))
            response = {"request_id": key, "result": result, "state": present(state)}
            db.execute("UPDATE operations SET status='complete',response=? WHERE id=? AND nonce=?", (json.dumps(response, ensure_ascii=False), key, reservation["nonce"]))
            return response
````

## Repository.abort

[원본 118번째 줄](../../../app/repository.py#L118)

실패한 자신의 예약만 재시도 가능 상태로 바꾼다. 새 예약을 지우지 않는다.

### 입력과 처리

```python
def abort(self, command, reservation):
```

### 실제 코드

````python
def abort(self, command, reservation):
        """실패한 자신의 예약만 재시도 가능 상태로 바꾼다. 새 예약을 지우지 않는다."""
        with self.transaction() as db:
            db.execute("UPDATE operations SET status='failed' WHERE id=? AND nonce=? AND status='pending'", (str(command.request_id), reservation["nonce"]))
````

