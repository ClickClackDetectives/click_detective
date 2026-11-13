"""SQLite 수사 저장·권한·요청 예약·원자적 확정. 모델 실행 동안 DB 잠금을 잡지 않는다."""

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import hmac
import json
from pathlib import Path
import secrets
import sqlite3
import time
from uuid import uuid4

from fastapi import HTTPException


def digest(value) -> str:
    """JSON 내용을 정규화해 같은 요청인지 비교한다. 값은 SQL에 바인딩한다."""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class Repository:
    """전체 수사 상태와 완료 요청을 저장한다. 모델 프롬프트·원본 검증 출력은 저장하지 않는다."""

    def __init__(self, path: Path):
        """게임 DB를 준비한다. 기존 기록은 삭제하지 않는다."""
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS games (id TEXT PRIMARY KEY, token_hash TEXT NOT NULL, revision INTEGER NOT NULL, state TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS operations (id TEXT PRIMARY KEY, game_id TEXT NOT NULL, digest TEXT NOT NULL, status TEXT NOT NULL, nonce TEXT, lease_until REAL, response TEXT)")

    @contextmanager
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

    def _game(self, db, game_id, token):
        """수사별 비밀 토큰을 검사한다. 다른 수사의 존재도 응답으로 노출하지 않는다."""
        row = db.execute("SELECT * FROM games WHERE id=?", (game_id,)).fetchone()
        hashed = hashlib.sha256(token.encode()).hexdigest()
        if row is None or not hmac.compare_digest(row["token_hash"], hashed):
            raise HTTPException(404, "수사를 찾을 수 없습니다.")
        return json.loads(row["state"])

    def get(self, game_id, token):
        """저장된 수사를 복원한다. 조회만으로 게임 상태를 바꾸지 않는다."""
        with self.transaction() as db:
            return self._game(db, game_id, token)

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

    def abort(self, command, reservation):
        """실패한 자신의 예약만 재시도 가능 상태로 바꾼다. 새 예약을 지우지 않는다."""
        with self.transaction() as db:
            db.execute("UPDATE operations SET status='failed' WHERE id=? AND nonce=? AND status='pending'", (str(command.request_id), reservation["nonce"]))
