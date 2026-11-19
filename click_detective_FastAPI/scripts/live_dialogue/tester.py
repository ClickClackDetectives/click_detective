"""실서버 대화 검사 사례와 보고서 생성을 조정한다."""

from datetime import datetime, timezone
from pathlib import Path

import httpx

from .case_runner import run_case
from .definitions import definitions
from .errors import LiveTestFailure
from .transport import LiveTransport


class LiveLlmTester:
    """실서버 대화 검사 사례와 보고서를 관리한다.

    Args:
        client (httpx.Client): HTTP 요청을 실행하는 클라이언트.
        api_key (str): 서버 인증에 사용할 비밀 API 키.
        data_dir (Path): 사건 JSON 데이터가 있는 디렉터리.
        expected_model_version (str | None): 응답에서 기대하는 정확한 모델 버전. None이면 일치 검사를 생략한다.

    Returns:
        LiveLlmTester: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(
        self,
        client: httpx.Client,
        api_key: str,
        data_dir: Path,
        expected_model_version: str | None = None,
    ):
        """HTTP 클라이언트를 외부에서 받아 단위 검사에서는 네트워크 없이 검사할 수 있다.

        Args:
            client (httpx.Client): HTTP 요청을 실행하는 클라이언트.
            api_key (str): 서버 인증에 사용할 비밀 API 키.
            data_dir (Path): 사건 JSON 데이터가 있는 디렉터리.
            expected_model_version (str | None): 응답에서 기대하는 정확한 모델 버전. None이면 일치 검사를 생략한다.

        Returns:
            None: 의존성과 초기 상태를 준비하며 값을 반환하지 않는다.
        """
        self.transport = LiveTransport(client, api_key)
        self.client = client
        self.headers = self.transport.headers
        self.secrets = self.transport.secrets
        self.data_dir = data_dir
        self.expected_model_version = expected_model_version
        self.report = {
            "started_at": datetime.now(timezone.utc).isoformat(),
            "mode": "live_http",
            "target_api": "POST /v1/games/{game_id}/interrogations",
            "server_started_by_script": False,
            "quantization": {
                "status": "not_measured_via_http",
                "explanation": "local 서버 로더는 4-bit NF4를 강제하지만 이 HTTP 검사는 GPU 가중치 형식을 직접 측정하지 않습니다.",
            },
            "preparation": [],
            "cases": [],
            "passed": False,
        }

    def redact(self, value):
        """보고서에 포함된 비밀값을 가린다.

        Args:
            value: 검사·변환하거나 비밀값을 가릴 입력 값.

        Returns:
            입력과 같은 구조의 값: 인증 정보와 알려진 비밀값을 가린 결과.
        """
        return self.transport.redact(value)

    def run_agents(self, inputs, *, progress=False):
        """게임 API 호출 없이 각 입력을 순서대로 검사한다.

        Args:
            inputs: 요청 UUID를 포함한 대화 입력 하나 또는 입력 목록.
            progress: 각 요청을 보내기 전에 진행 상황을 출력할지 여부.

        Returns:
            dict: 요청·응답·시간 및 대화 응답 검사를 포함한 실서버 보고서.
        """
        path = "/internal/agent-test"
        self.report["mode"] = "live_agents_only"
        self.report["target_api"] = f"POST {path}"
        inputs = [inputs] if isinstance(inputs, dict) else inputs
        for index, body in enumerate(inputs, 1):
            if progress:
                print(f"에이전트 검사 {index}/{len(inputs)}", flush=True)
            self.run_agent_case(path, f"agents-{index:03d}", body)
        self.report["passed"] = bool(self.report["cases"]) and all(
            case["passed"] for case in self.report["cases"]
        )
        self.report["completed_at"] = datetime.now(timezone.utc).isoformat()
        return self.report

    def run_agent_case(self, path, name, body):
        """한 입력의 HTTP 왕복과 검사 결과를 보고서에 추가한다.

        Args:
            path: 에이전트 검사 API 경로.
            name: 보고서에 표시할 사례 이름.
            body: 대화 그래프에 전달할 요청 본문.

        Returns:
            None: 사례 결과를 보고서에 기록한다.
        """
        case = {
            "name": name,
            "description": "전처리·추론·검증 에이전트 단독 검사",
            "request_id": body["request_id"],
            "exchanges": [],
            "checks": {},
            "passed": False,
        }
        self.report["cases"].append(case)
        try:
            output = self.transport.exchange(
                case["exchanges"], "POST", path, body, purpose="agent_test"
            )
            used_ids = output.get("used_fact_ids")
            required_ids = body.get("required_fact_ids", [])
            allowed_ids = [fact["id"] for fact in body.get("allowed_facts", [])]
            reply = output.get("reply")
            checks = {
                "same_request_id": output.get("request_id") == body["request_id"],
                "matching_context": output.get("suspect_id") == body["suspect_id"]
                and output.get("state_revision") == body["state_revision"],
                "generated_reply": output.get("finish_reason") == "stop"
                and isinstance(reply, str)
                and bool(reply.strip()),
                "approved_fact_ids": isinstance(used_ids, list)
                and all(fact in used_ids for fact in required_ids)
                and all(fact in allowed_ids for fact in used_ids),
            }
            if self.expected_model_version:
                checks["expected_model_version"] = (
                    output.get("model_version") == self.expected_model_version
                )
            case["checks"] = checks
            case["passed"] = all(checks.values())
            if not case["passed"]:
                case["error"] = ", ".join(key for key, ok in checks.items() if not ok)
        except LiveTestFailure as error:
            case["error"] = str(error)

    def exchange(
        self, rows, method, path, body=None, token=None, purpose="preparation"
    ):
        """HTTP 요청을 보내고 왕복 기록을 남긴다.

        Args:
            rows: HTTP 왕복 기록을 추가할 목록.
            method: HTTP 요청 메서드. 예: GET, POST.
            path: 저장 파일 경로나 HTTP 요청 경로.
            body: 전송하거나 비교할 JSON 요청 본문.
            token: 수사 접근 토큰 또는 요청 문맥 복원용 토큰.
            purpose: 모델 호출 목적. dialogue는 생성, verification은 검증이다.

        Returns:
            dict: 성공한 HTTP 응답의 JSON 객체. 왕복 기록은 rows에도 추가한다.
        """
        return self.transport.exchange(rows, method, path, body, token, purpose)

    def definitions(self, catalog):
        """사건 데이터에서 실행할 검사 사례를 구성한다.

        Args:
            catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

        Returns:
            dict: profile, movement, evidence 세 가지 심문 사례.
        """
        return definitions(catalog, self.data_dir)

    def run_case(self, name, definition, catalog):
        """독립 수사에서 한 심문 사례를 실행하고 결과를 기록한다.

        Args:
            name: 읽을 파일 또는 실행할 사례의 이름.
            definition: 질문, 준비 자료와 기대 결과를 담은 검사 사례.
            catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

        Returns:
            None: 결과는 상태 갱신·기록 또는 예외로 전달하며 값을 반환하지 않는다.
        """
        run_case(self, name, definition, catalog)

    def run(self, selected):
        """준비 조회를 한 번 수행하고 선택한 심문 사례만 실행한다.

        Args:
            selected: 실행할 실서버 검사 사례 이름 목록.

        Returns:
            dict: 선택한 사례의 검사 결과와 완료 시각을 담은 보고서.
        """
        try:
            self.exchange(self.report["preparation"], "GET", "/healthz")
            catalog = self.exchange(self.report["preparation"], "GET", "/v1/catalog")
            definitions = self.definitions(catalog)
            self.report["case_data"] = {
                "case_id": catalog["caseId"],
                "scenario_version": catalog["scenarioVersion"],
                "sources": [
                    "data/case/evidence.json",
                    "data/case/findings.private.json",
                    "GET /v1/catalog",
                ],
            }
            for name in selected:
                self.run_case(name, definitions[name], catalog)
        except (LiveTestFailure, OSError, KeyError, TypeError, ValueError) as error:
            self.report["error"] = str(error)
        self.report["passed"] = bool(self.report["cases"]) and all(
            case["passed"] for case in self.report["cases"]
        )
        self.report["completed_at"] = datetime.now(timezone.utc).isoformat()
        return self.report
