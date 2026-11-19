"""게임 상태에 의존하지 않는 에이전트 검사 입력."""

import json
from uuid import uuid4

SCENARIOS = (
    (
        "이서진",
        "도서관 방문자",
        "차분한 존댓말",
        "도서관",
        "예약한 책을 수령하러 왔습니다.",
        "반납함 옆에 파란 상자가 있었습니다.",
        "사서에게서 열람실이 오후 여섯 시에 닫는다고 들었습니다.",
    ),
    (
        "박현우",
        "기차역 안내원",
        "짧고 명확한 존댓말",
        "기차역",
        "오후 교대 근무를 시작하러 왔습니다.",
        "2번 승강장 안내판이 꺼져 있었습니다.",
        "기관사에게서 첫 열차가 10분 지연된다고 들었습니다.",
    ),
    (
        "정하은",
        "전시 설치 기사",
        "격식을 갖춘 존댓말",
        "전시장",
        "작품 조명을 점검하러 왔습니다.",
        "입구 맞은편에 액자 세 점이 놓여 있었습니다.",
        "기획자에게서 개막 시간이 오전 11시로 바뀌었다고 들었습니다.",
    ),
    (
        "김도윤",
        "시장 배달원",
        "친근한 존댓말",
        "전통시장",
        "채소 두 상자를 배달하러 왔습니다.",
        "시장 북쪽 입구에 흰색 손수레가 있었습니다.",
        "상인에게서 남쪽 통로가 공사 중이라고 들었습니다.",
    ),
    (
        "최윤아",
        "체육관 관리인",
        "간결한 존댓말",
        "체육관",
        "저녁 대관 준비를 하러 왔습니다.",
        "관중석 첫 줄에 젖은 수건이 있었습니다.",
        "코치에게서 오늘 참가자가 12명이라고 들었습니다.",
    ),
    (
        "서민재",
        "음향 기사",
        "실무적인 존댓말",
        "공연장",
        "공연 전 마이크를 점검하러 왔습니다.",
        "무대 왼편의 스피커 두 대가 켜져 있었습니다.",
        "무대 감독에게서 리허설이 오후 네 시에 시작한다고 들었습니다.",
    ),
    (
        "한지우",
        "온실 연구원",
        "신중한 존댓말",
        "온실",
        "묘목의 생장 상태를 기록하러 왔습니다.",
        "3번 화분의 이름표가 바닥에 떨어져 있었습니다.",
        "관리자에게서 새 배양토가 다음 주에 도착한다고 들었습니다.",
    ),
    (
        "오수현",
        "숙소 직원",
        "공손한 존댓말",
        "숙소",
        "로비의 분실물 목록을 확인하러 왔습니다.",
        "현관 안쪽에 검은 우산 두 개가 있었습니다.",
        "동료에게서 204호 투숙객이 오전 아홉 시에 출발했다고 들었습니다.",
    ),
    (
        "윤태준",
        "정비 기사",
        "담담한 존댓말",
        "정비소",
        "예약된 차량의 타이어를 교체하러 왔습니다.",
        "정비대 위에 공구 상자 하나가 열려 있었습니다.",
        "접수 담당자에게서 차량이 30분 늦게 도착한다고 들었습니다.",
    ),
    (
        "임소라",
        "우체국 직원",
        "또렷한 존댓말",
        "우체국",
        "오전에 들어온 등기 우편을 분류하러 왔습니다.",
        "창구 옆 선반에 소포 네 개가 올라와 있었습니다.",
        "집배원에게서 동쪽 배달 구역의 순서가 바뀌었다고 들었습니다.",
    ),
)

QUESTIONS = (
    ("방문 목적", "{place}에 오신 목적을 알려 주세요.", (0,)),
    ("직접 관찰", "{place}에서 직접 본 것을 설명해 주세요.", (1,)),
    ("전해 들은 내용", "다른 사람에게서 어떤 이야기를 들으셨나요?", (2,)),
    ("목적과 관찰", "오신 이유와 현장에서 본 것을 함께 말해 주세요.", (0, 1)),
    ("목적과 전언", "방문 목적과 전해 들은 내용을 각각 알려 주세요.", (0, 2)),
    ("관찰과 전언", "본 것과 들은 것을 나눠서 말씀해 주세요.", (1, 2)),
    ("종합 진술", "왜 오셨고, 무엇을 직접 보거나 전해 들으셨나요?", (0, 1, 2)),
    ("기록 대조", "제시한 기록을 참고해 직접 본 상황을 설명해 주세요.", (1,)),
    ("후속 질문", "방문 목적은 알겠습니다. 그곳에서 무엇을 보셨나요?", (1,)),
    (
        "출처 확인",
        "조금 전 진술에 이어, 누구에게 어떤 이야기를 들었는지 알려 주세요.",
        (2,),
    ),
    ("관찰 범위", "현장에 없던 사람에게 직접 확인한 사실만 알려 주시겠어요?", (1,)),
    ("간결한 재진술", "방문 목적과 들은 내용을 짧게 정리해 주세요.", (0, 2)),
)


def default_agent_inputs():
    """시나리오와 질문을 교차해 다양한 승인 문맥을 구성한다.

    Args:
        없음.

    Returns:
        list[dict]: 서로 다른 인물·질문·필수 사실 조합 120건.
    """
    fact_ids = ("visit-reason", "observation", "secondhand")
    inputs = []
    for number, (name, role, style, place, *texts) in enumerate(SCENARIOS, 1):
        for category, question, required in QUESTIONS:
            history = []
            if category in {"후속 질문", "출처 확인"}:
                history = [
                    {"role": "user", "text": f"{place}에 왜 오셨나요?"},
                    {"role": "suspect", "text": texts[0]},
                ]
            materials = []
            if category == "기록 대조":
                materials = [
                    {
                        "kind": "evidence",
                        "id": "observation-record",
                        "code": "E-01",
                        "title": f"{place} 현장 기록",
                        "allowed_text": texts[1],
                    }
                ]
            inputs.append(
                {
                    "game_id": "agent-test",
                    "case_id": "agent-test",
                    "scenario_version": "agent-test",
                    "state_revision": 1 if history else 0,
                    "turn_index": 2 if history else 1,
                    "suspect_id": f"sample-person-{number:02d}",
                    "phase": 2 if materials else 1,
                    "question": question.format(place=place),
                    "persona": {"name": name, "role": role, "speech_style": style},
                    "allowed_facts": [
                        {"id": fact_id, "text": text, "nature": nature}
                        for fact_id, text, nature in zip(
                            fact_ids,
                            texts,
                            ("본인 진술", "직접 목격", "전언"),
                            strict=True,
                        )
                    ],
                    "required_fact_ids": [fact_ids[index] for index in required],
                    "history": history,
                    "presented_materials": materials,
                }
            )
    return inputs


def load_agent_inputs(paths, limit=None):
    """기본 사례 또는 JSON 파일을 읽고 요청별 새 UUID를 부여한다.

    Args:
        paths: 입력 파일 경로 목록. None이나 빈 목록이면 기본 입력을 사용한다.
        limit: 실행할 최대 입력 수. None이면 전체를 사용한다.

    Returns:
        list[dict]: 요청 UUID가 부여된 비어 있지 않은 입력 목록.
    """
    inputs = [] if paths else default_agent_inputs()
    for path in paths or ():
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data if isinstance(data, list) else [data]
        if not rows or any(not isinstance(row, dict) for row in rows):
            raise ValueError(
                f"{path}: 입력은 JSON 객체 또는 비어 있지 않은 객체 배열이어야 합니다."
            )
        inputs.extend(rows)
    return [body | {"request_id": str(uuid4())} for body in inputs[:limit]]
