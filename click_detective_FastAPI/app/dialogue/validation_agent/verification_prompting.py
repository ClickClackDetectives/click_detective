"""전체 승인 문맥을 유지하면서 검사할 문장 묶음과 재요청 지시를 만든다."""

import json

from .prompt import build_verification_messages
from .semantic_verification import candidate_sentences


def build_batch_messages(request, settings, reply, batch):
    """이번 배치에서 확인할 항목을 검증 프롬프트에 지정한다.

    Args:
        request: 원래 승인 사실과 필수 사실 ID를 담은 대화 요청.
        settings: 이력 개수 등 프롬프트 구성 설정.
        reply: 검사할 후보 대사 원문.
        batch: 이번 호출에서 검사할 승인 문장 목록.

    Returns:
        list[dict[str, str]]: 전체 승인 사실과 이번 검사 항목을 담은 프롬프트.
    """
    messages = build_verification_messages(request, settings, reply)
    context = json.loads(messages[1]["content"])
    context["verification_units"] = [
        {"index": int(unit.id.removeprefix("unit-")), "fact_id": unit.fact_id}
        for unit in batch
    ]
    messages[1]["content"] = json.dumps(
        context, ensure_ascii=False, separators=(",", ":")
    )
    expected_ids = [int(unit.id.removeprefix("unit-")) for unit in batch]
    messages.append(
        {
            "role": "user",
            "content": (
                f"이번 checks의 index는 {json.dumps(expected_ids)}를 빠짐없이 각각 한 번씩 반환하세요. "
                f"checks는 정확히 {len(expected_ids)}개입니다. fact_id 개수가 아니라 검증 문장 개수입니다. "
                "각 문장에 대해 true이면 실제 후보 문장 번호, false이면 빈 배열 []을 사용하세요."
            ),
        }
    )
    return messages


def build_report_retry(reply, batch, error):
    """같은 후보에 대해 올바른 형식의 검사표를 다시 요청한다.

    Args:
        reply: 재생성하지 않고 그대로 검사할 후보 대사.
        batch: 빠짐없이 확인해야 할 승인 문장 목록.
        error: 직전 보고서의 형식 오류 코드와 상세 사유.

    Returns:
        dict[str, str]: 검증 프롬프트 끝에 추가할 사용자 역할 지시문.
    """
    expected_ids = [int(unit.id.removeprefix("unit-")) for unit in batch]
    return {
        "role": "user",
        "content": (
            f"검증 형식 오류: {error}/{error.detail}. 필요한 checks index 목록: {json.dumps(expected_ids)}. "
            f"선택 가능한 후보 문장 번호: {[part.id for part in candidate_sentences(reply)]}. "
            "같은 후보를 다시 검사하고 JSON 객체 하나만 반환하세요. "
            "checks=[index, true, [후보문장번호]] 또는 [index, false, []]입니다. "
            "false 판정에는 근거 번호를 절대로 넣지 마세요. 모든 index를 검사하세요."
        ),
    }
