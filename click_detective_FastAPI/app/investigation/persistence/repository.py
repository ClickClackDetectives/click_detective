"""SQLite 수사 저장·권한·요청 예약·원자적 확정. 모델 실행 동안 DB 잠금을 잡지 않는다."""

import hashlib
import hmac
import json
import secrets
import time
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException

from app.investigation.persistence.storage import InvestigationStorage, digest


class Repository:
    """전체 수사 상태와 완료 요청을 저장한다. 모델 프롬프트·원본 검증 출력은 저장하지 않는다.

    Args:
        path (Path): 수사 상태와 요청 기록을 저장할 SQLite 파일 경로.

    Returns:
        Repository: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, path: Path):
        """게임 DB를 준비한다. 기존 기록은 삭제하지 않는다.

        Args:
            path (Path): 수사 상태와 요청 기록을 저장할 SQLite 파일 경로.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.storage = InvestigationStorage(path)
        with self.transaction() as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS games (id TEXT PRIMARY KEY, token_hash TEXT NOT NULL, revision INTEGER NOT NULL, state TEXT NOT NULL)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS operations (id TEXT PRIMARY KEY, game_id TEXT NOT NULL, digest TEXT NOT NULL, status TEXT NOT NULL, nonce TEXT, lease_until REAL, response TEXT)"
            )

    def transaction(self):
        """짧은 쓰기 트랜잭션을 제공한다. 실패 시 롤백하고 연결을 항상 닫는다.

        Args:
            없음.

        Returns:
            ContextManager: SQLite 연결을 제공하고 성공 시 commit, 실패 시 rollback하는 문맥 관리자.
        """
        return self.storage.transaction()

    def _game(self, db, game_id, token):
        """수사별 비밀 토큰을 검사한다. 다른 수사의 존재도 응답으로 노출하지 않는다.

        Args:
            db: 현재 트랜잭션의 SQLite 연결.
            game_id: 조회하거나 변경할 수사의 식별자.
            token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.

        Returns:
            dict: 소유권을 확인한 저장 상태. 권한이 없으면 HTTPException을 낸다.
        """
        row = db.execute("SELECT * FROM games WHERE id=?", (game_id,)).fetchone()
        hashed = hashlib.sha256(token.encode()).hexdigest()
        if row is None or not hmac.compare_digest(row["token_hash"], hashed):
            raise HTTPException(404, "수사를 찾을 수 없습니다.")
        return json.loads(row["state"])

    def get(self, game_id, token):
        """저장된 수사를 복원한다. 조회만으로 게임 상태를 바꾸지 않는다.

        Args:
            game_id: 조회하거나 변경할 수사의 식별자.
            token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.

        Returns:
            dict: 접근 권한을 확인한 수사의 저장 상태.
        """
        with self.transaction() as db:
            return self._game(db, game_id, token)

    def create(self, request, factory, present):
        """초기 수사와 재전송 응답을 같은 트랜잭션에서 저장한다.

        Args:
            request: 생성할 사건 ID와 버전, 요청 UUID를 담은 새 수사 입력.
            factory: 게임 ID를 받아 초기 상태를 만드는 함수.
            present: 내부 상태를 공개 응답으로 변환하는 함수.

        Returns:
            dict: 수사 ID, 접근 토큰과 공개 초기 상태 또는 저장된 동일 요청 결과.
        """
        key = str(request.request_id)
        body_hash = digest(
            {"action": "create", "body": request.model_dump(mode="json")}
        )
        with self.transaction() as db:
            previous = db.execute(
                "SELECT * FROM operations WHERE id=?", (key,)
            ).fetchone()
            if previous:
                if previous["digest"] != body_hash:
                    raise HTTPException(409, "같은 요청 UUID의 내용이 다릅니다.")
                return json.loads(previous["response"])
            game_id = str(uuid4())
            token = secrets.token_urlsafe(32)
            state = factory(game_id)
            result = {"game_id": game_id, "game_token": token, "state": present(state)}
            db.execute(
                "INSERT INTO games VALUES (?,?,?,?)",
                (
                    game_id,
                    hashlib.sha256(token.encode()).hexdigest(),
                    0,
                    json.dumps(state, ensure_ascii=False),
                ),
            )
            db.execute(
                "INSERT INTO operations VALUES (?,?,?,'complete',NULL,NULL,?)",
                (key, game_id, body_hash, json.dumps(result, ensure_ascii=False)),
            )
            return result

    def reserve(self, game_id, token, command, action, lease_seconds):
        """실행권을 예약하고 상태 사본을 반환한다. 완료 재전송은 revision 검사보다 먼저 처리한다.

        Args:
            game_id: 조회하거나 변경할 수사의 식별자.
            token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
            action: 실행할 수사 행동 이름. 예: interrogate, examine.
            lease_seconds: 작업 예약을 유효하게 유지할 초 단위 시간.

        Returns:
            dict: 예약 식별값·상태 사본·버전 또는 동일 요청의 캐시된 응답.
        """
        key = str(command.request_id)
        body_hash = digest(
            {
                "game_id": game_id,
                "action": action,
                "body": command.model_dump(mode="json"),
            }
        )
        with self.transaction() as db:
            state = self._game(db, game_id, token)
            operation = db.execute(
                "SELECT * FROM operations WHERE id=?", (key,)
            ).fetchone()
            if operation:
                if operation["digest"] != body_hash:
                    raise HTTPException(409, "같은 요청 UUID의 내용이 다릅니다.")
                if operation["status"] == "complete":
                    return {"cached": json.loads(operation["response"])}
                if (
                    operation["status"] == "pending"
                    and operation["lease_until"] > time.time()
                ):
                    raise HTTPException(409, "operation_in_progress")
            if state["revision"] != command.expected_revision:
                raise HTTPException(409, "state_revision_conflict")
            nonce = str(uuid4())
            db.execute(
                "INSERT INTO operations VALUES (?,?,?,'pending',?,?,NULL) ON CONFLICT(id) DO UPDATE SET status='pending',nonce=excluded.nonce,lease_until=excluded.lease_until",
                (key, game_id, body_hash, nonce, time.time() + lease_seconds),
            )
            return {
                "state": deepcopy(state),
                "nonce": nonce,
                "revision": state["revision"],
            }

    def commit(self, game_id, command, reservation, state, result, present):
        """예약 소유권과 최신 revision을 다시 확인하고 결과·상태를 한 번 확정한다.

        Args:
            game_id: 조회하거나 변경할 수사의 식별자.
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
            reservation: 작업의 상태 사본, 예약 식별값과 기준 버전.
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            result: 행동 처리 결과로 공개할 정보.
            present: 내부 상태를 공개 응답으로 변환하는 함수.

        Returns:
            dict: 요청 ID, 행동 결과와 저장된 공개 상태.
        """
        key = str(command.request_id)
        with self.transaction() as db:
            operation = db.execute(
                "SELECT * FROM operations WHERE id=?", (key,)
            ).fetchone()
            row = db.execute(
                "SELECT revision,state FROM games WHERE id=?", (game_id,)
            ).fetchone()
            if (
                operation is None
                or operation["nonce"] != reservation["nonce"]
                or operation["status"] != "pending"
            ):
                raise HTTPException(409, "operation_reservation_conflict")
            if row["revision"] != reservation["revision"]:
                raise HTTPException(409, "state_changed_during_generation")
            previous = json.loads(row["state"])
            if state != previous:
                state["revision"] = previous["revision"] + 1
                db.execute(
                    "UPDATE games SET state=?,revision=? WHERE id=?",
                    (json.dumps(state, ensure_ascii=False), state["revision"], game_id),
                )
            response = {"request_id": key, "result": result, "state": present(state)}
            db.execute(
                "UPDATE operations SET status='complete',response=? WHERE id=? AND nonce=?",
                (json.dumps(response, ensure_ascii=False), key, reservation["nonce"]),
            )
            return response

    def abort(self, command, reservation):
        """실패한 자신의 예약만 재시도 가능 상태로 바꾼다. 새 예약을 지우지 않는다.

        Args:
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.
            reservation: 작업의 상태 사본, 예약 식별값과 기준 버전.

        Returns:
            None: 반환값 없음.
        """
        with self.transaction() as db:
            db.execute(
                "UPDATE operations SET status='failed' WHERE id=? AND nonce=? AND status='pending'",
                (str(command.request_id), reservation["nonce"]),
            )
