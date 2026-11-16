"""모델에 의미 검증 보고서를 요청하고 형식 오류만 재요청한다."""

import json
from time import perf_counter

from pydantic import ValidationError

from ..diagnostics import trace_event
from ..schemas import CharacterReplyRequest
from ..state import OutputRejected
from .evidence_checks import check_report_evidence
from .report_policy import (
    VERIFICATION_FORMAT_CODES,
    combine_reports,
    reject_semantic_errors,
)
from .semantic_verification import SemanticReport
from .verification_prompting import build_batch_messages, build_report_retry
from .verification_units import build_verification_units


class VerificationReporter:
    """승인 문장을 나누어 검사하고 보고서 형식 오류에 한해 재요청한다.

    Args:
        settings: 배치 크기와 보고서 요청 횟수 설정.
        model: 생성에 사용한 것과 같은 모델 실행 객체.

    Returns:
        VerificationReporter: 의미 검증 보고서 요청을 담당하는 객체.
    """

    def __init__(self, settings, model):
        """검증 호출에 사용할 설정과 모델을 보관한다.

        Args:
            settings: 배치 크기와 보고서 요청 횟수 설정.
            model: 검증 목적의 프롬프트를 실행할 모델.

        Returns:
            None: 의존성을 보관한다.
        """
        self.settings = settings
        self.model = model

    async def request_report(
        self, request: CharacterReplyRequest, reply: str
    ) -> tuple[SemanticReport, set[str]]:
        """모든 문장 묶음을 검사하고 전체 보고서와 확인한 사실 ID를 반환한다.

        Args:
            request: 공개가 승인된 사실 전체와 필수 사실 ID를 담은 요청.
            reply: 의미를 검사할 후보 대사 원문.

        Returns:
            tuple[SemanticReport, set[str]]: 통합 보고서와 모든 문장이 확인된 사실 ID.
        """
        units = build_verification_units(request)
        batch_size = self.settings.verification_batch_size
        batches = [
            units[index : index + batch_size]
            for index in range(0, len(units), batch_size)
        ] or [[]]
        reports = []
        for batch_index, batch in enumerate(batches):
            report = await self._request_batch(request, reply, batch, batch_index)
            reports.append(report)
        combined = combine_reports(reports)
        return combined, check_report_evidence(combined, request, reply)

    async def _request_batch(self, request, reply, batch, batch_index):
        """같은 후보를 검사하며 보고서의 형식 오류만 제한 횟수 안에서 재요청한다.

        Args:
            request: 원래 승인 계획이 포함된 요청.
            reply: 이번 검사 동안 변경하지 않을 후보 대사.
            batch: 이번 모델 호출에서 확인할 승인 문장 목록.
            batch_index: 진단에 기록할 0부터 시작하는 배치 번호.

        Returns:
            SemanticReport: 형식·근거·의미 조건을 모두 통과한 배치 보고서.
        """
        messages = build_batch_messages(request, self.settings, reply, batch)
        last_error = OutputRejected("invalid_verification_output")
        for attempt in range(self.settings.verification_attempts):
            current_messages = list(messages)
            if attempt:
                current_messages.append(build_report_retry(reply, batch, last_error))
            started = perf_counter()
            raw = await self.model.generate(current_messages, purpose="verification")
            trace_event(
                "verification",
                batch=batch_index + 1,
                attempt=attempt + 1,
                elapsed_ms=round((perf_counter() - started) * 1000, 2),
            )
            try:
                report = self._parse_report(raw, request, reply, batch)
            except OutputRejected as error:
                if str(error) not in VERIFICATION_FORMAT_CODES:
                    raise
                last_error = error
                trace_event(
                    "verification_rejected",
                    batch=batch_index + 1,
                    code=str(error),
                    detail=error.detail,
                )
                continue
            # 의미상 거절은 보고서 형식 재시도로 바꾸지 않는다.
            reject_semantic_errors(report)
            return report
        raise last_error

    @staticmethod
    def _parse_report(raw, request, reply, batch):
        """보고서를 파싱하고 검사 항목과 실제 근거 문장 번호를 검증한다.

        Args:
            raw: 검증 모델이 출력한 JSON 원문.
            request: 전체 승인 사실을 담은 요청.
            reply: 근거 문장의 번호를 확인할 후보 대사.
            batch: 보고서가 빠짐없이 확인해야 하는 승인 문장 목록.

        Returns:
            SemanticReport: JSON·스키마·항목·근거 형식을 통과한 보고서.
        """
        try:
            data = json.loads(raw)
        except (ValueError, TypeError):
            raise OutputRejected("invalid_verification_json") from None
        try:
            report = SemanticReport.model_validate(data)
        except ValidationError:
            raise OutputRejected("invalid_verification_schema") from None
        check_report_evidence(report, request, reply, batch)
        return report
