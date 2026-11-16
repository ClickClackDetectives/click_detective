"""후보 대사가 승인 의미를 보존하는지 최종 판정한다."""

from ..diagnostics import trace_event
from ..reply_validation import validate_generation
from ..schemas import CharacterReplyRequest, CharacterReplyResponse
from ..state import OutputRejected
from .critical_facts import critical_claim_error
from .report_policy import reject_semantic_errors
from .verification_reports import VerificationReporter


class SemanticVerifier:
    """규칙 검사와 모델 보고서를 결합해 대사의 의미 보존을 판정한다.

    Args:
        settings: 모델 실행과 검색에 사용할 설정.
        model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

    Returns:
        SemanticVerifier: 위 역할을 수행하도록 생성된 객체.
    """

    def __init__(self, settings, model):
        """사용할 의존성과 초기 상태를 준비한다.

        Args:
            settings: 모델 실행과 검색에 사용할 설정.
            model: 대사 생성과 의미 검증에 사용할 모델 실행 객체.

        Returns:
            None: 필요한 설정과 초기값을 저장한다.
        """
        self.reporter = VerificationReporter(settings, model)

    async def verify(
        self, request: CharacterReplyRequest, response: CharacterReplyResponse
    ) -> CharacterReplyResponse:
        """별도 모델 호출의 의미 판정을 확인한다. 형식 재시도 후에도 불확실하면 거절한다.

        Args:
            request (CharacterReplyRequest): 승인 사실, 필수 사실 ID와 인물·대화 문맥을 담은 요청.
            response (CharacterReplyResponse): 검사하거나 저장할 최종 대사 응답.

        Returns:
            CharacterReplyResponse: 의미 검증 결과로 사실 ID를 확정한 응답.
        """
        guard = critical_claim_error(request, response.reply)
        if guard:
            trace_event("critical_claim_rejected", code=guard)
            raise OutputRejected(guard)
        report, supported_ids = await self.reporter.request_report(
            request, response.reply
        )
        reject_semantic_errors(report)
        if not set(request.required_fact_ids).issubset(supported_ids):
            raise OutputRejected("missing_fact_meaning")
        if response.used_fact_ids and supported_ids != set(response.used_fact_ids):
            raise OutputRejected("fact_coverage_mismatch")
        # 최종 사실 ID는 생성자의 자기 신고가 아닌 별도 검증 결과에서 만든다.
        verified_ids = []
        for fact in request.allowed_facts:
            if fact.id in supported_ids:
                verified_ids.append(fact.id)
        verified_response = response.model_copy(update={"used_fact_ids": verified_ids})
        validate_generation(request, verified_response, require_verbatim=False)
        return verified_response
