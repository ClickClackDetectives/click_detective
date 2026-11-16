"""자료 열람·진술·쟁점·추론·단계·고발 규칙. LLM은 이 상태를 직접 수정하지 않는다."""

from copy import deepcopy
from datetime import datetime, timezone

from fastapi import HTTPException

from .accusation import AccusationRules
from .evidence import examine, infer, readable_source
from .testimony import record_plan


def utc_now():
    """저장 시각을 타임존이 있는 ISO 문자열로 만든다.

    Args:
        없음.

    Returns:
        str: UTC 시간대 정보가 포함된 현재 시각의 ISO 문자열.
    """
    return datetime.now(timezone.utc).isoformat()


class Engine:
    """정적 데이터와 실제 획득 기록만으로 판정하는 Python 게임 엔진.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

    Returns:
        Engine: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, catalog):
        """내부 사건·규칙 저장소를 연결한다.

        Args:
            catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.catalog = catalog
        self.accusation = AccusationRules(catalog)

    def initial(self, game_id):
        """새 수사는 새로운 ID로 시작한다. 예전 수사에 늦은 응답이 반영되지 않는다.

        Args:
            game_id: 조회하거나 변경할 수사의 식별자.

        Returns:
            dict: 질문과 획득 자료가 초기화된 새 수사 상태.
        """
        state = deepcopy(self.catalog.read("initial-state.json")["state"])
        state.update(
            id=game_id,
            startedAt=utc_now(),
            revision=0,
            scenarioVersion=self.catalog.version,
        )
        return state

    def require_active(self, state):
        """버전 변경과 종결 후 변경 요청을 거절한다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.

        Returns:
            None: 반환값 없음.
        """
        if state["scenarioVersion"] != self.catalog.version:
            raise HTTPException(409, "scenario_version_conflict")
        if state["verdict"]:
            raise HTTPException(409, "이미 종결된 사건입니다.")

    def examine(self, state, command):
        """현재 단계의 실제 자료만 열람한다. 중복은 개수·revision을 늘리지 않는다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

        Returns:
            dict: 열람 처리한 원본 자료의 식별자.
        """
        return examine(self.catalog, state, command)

    def record_plan(self, state, plan, response):
        """검증된 응답이 나온 뒤에만 질문·대화·쟁점·진술을 일괄 반영한다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            plan: 게임 규칙이 승인한 사실과 기록 예정 정보를 담은 계획.
            response: 검사하거나 저장할 최종 대사 응답.

        Returns:
            dict: 기록한 대사, 종료 사유, 모델 버전과 사용 사실 ID.
        """
        return record_plan(self.catalog, state, plan, response)

    def readable_source(self, state, source):
        """존재뿐 아니라 실제 획득·단계 조건도 검사한다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            source: 열람 가능 여부를 검사할 자료 종류와 식별자.

        Returns:
            None: 출처 열람 조건을 확인한다. 미획득 자료면 HTTPException을 낸다.
        """
        return readable_source(self.catalog, state, source)

    def infer(self, state, command):
        """직접 선택한 정확한 조합과 단계가 일치하면 고정 결론을 만든다. LLM은 사용하지 않는다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

        Returns:
            dict: 확보한 출처 조합으로 만든 추론 문서의 사본.
        """
        return infer(self.catalog, state, command)

    def readiness(self, state):
        """입증 진행 개수를 계산한다. 진행도와 무관하게 미종결 수사는 고발할 수 있다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.

        Returns:
            dict: 확보한 필수 추론·쟁점 수와 고발 가능 여부.
        """
        rules = self.catalog.rules["accusation"]
        inference = sum(
            key in state["derivedEvidence"] for key in rules["requiredInferenceIds"]
        )
        findings = sum(
            flag in state["revealed"] for flag in rules["requiredFindingFlags"]
        )
        return {
            "inference": inference,
            "findings": findings,
            "eligible": not bool(state["verdict"]),
        }

    def advance(self, state, command):
        """단계 전환 조건을 확인한 뒤 자동 자료와 단계를 함께 변경한다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

        Returns:
            dict: 변경된 조사 단계.
        """
        requirements = self.catalog.rules["secondRound"]["requirements"]
        if state["phase"] != 1:
            raise HTTPException(409, "이미 2차 조사가 진행 중입니다.")
        if (
            len(state["derivedEvidence"]) < requirements["inference"]
            or len(set(state["contradictions"])) < requirements["findings"]
        ):
            raise HTTPException(
                422, "2차 수사에는 추론 증거 2개와 심문 쟁점 2개 이상이 필요합니다."
            )
        state["phase"] = 2
        for key in self.catalog.rules["secondRound"]["automaticEvidenceIds"]:
            if key not in state["examined"]:
                state["examined"].append(key)
        return {"phase": 2}

    def covered(self, state, ids):
        """제출한 추론이 뒷받침하는 원본 증거를 구한다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            ids: 실제 획득하여 제출한 추론 증거 식별자 목록.

        Returns:
            set[str]: 제출한 추론이 뒷받침하는 실제 열람 원본 증거 ID.
        """
        return self.accusation.covered(state, ids)

    def accuse(self, state, command):
        """고발 규칙 담당자에게 제출 근거와 정답 선택 평가를 맡긴다.

        Args:
            state: 질문·대화·획득 자료를 담은 현재 수사 상태.
            command: 사용자 행동과 요청 ID, 예상 상태 버전을 담은 입력.

        Returns:
            dict: 정답 일치, 점수, 제출 근거 평가와 사건 해설.
        """
        return self.accusation.accuse(state, command)
