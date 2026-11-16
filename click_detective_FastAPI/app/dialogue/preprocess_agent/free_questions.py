"""인정 상태와 자유 질문에 맞는 공개 진술을 고른다."""

import re
from copy import deepcopy


def movement(catalog, suspect, flags):
    """인정 플래그 조합에 맞는 동선 원문만 선택한다. 후보 전체를 모델에 주지 않는다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        suspect: 심문 대상 인물의 식별자.
        flags: 현재까지 인정되거나 공개된 쟁점 식별자 목록.

    Returns:
        list[dict]: 현재 인정 상태에 맞는 동선 진술.
    """
    variants = catalog.statement_people[suspect]["movementVariants"]
    relevant = set()
    for variant in variants:
        for flag in variant["recognizedFlags"]:
            relevant.add(flag)
    selected = set(flags) & relevant
    return deepcopy(
        next(
            variant["entries"]
            for variant in variants
            if set(variant["recognizedFlags"]) == selected
        )
    )


def free_entries(catalog, suspect, question, flags):
    """자유 질문을 공개 동선·관계·이미 인정한 진술에 연결한다. 미승인 비밀은 선택하지 않는다.

    Args:
        catalog: 사건 원문, 인물과 게임 규칙을 제공하는 객체.
        suspect: 심문 대상 인물의 식별자.
        question: 사용자가 입력한 질문 원문.
        flags: 현재까지 인정되거나 공개된 쟁점 식별자 목록.

    Returns:
        list[dict]: 질문과 관련하여 공개 가능한 진술. 없으면 빈 목록.
    """
    if re.search(r"대학|학력|레시피|프롬프트|지침|역할.*바꿔|정답.*알려", question):
        return []
    movement_entries = movement(catalog, suspect, flags)
    # 이미 인정한 쟁점은 관련 질문에 답할 수 있다. 새 인정은 앞의 자료 조건만 결정한다.
    flag_patterns = {
        "gang_drug": "약|수면|와인",
        "gang_visit": "차용|꽃병|재방문|원본",
        "yoon_money": "장부|횡령|빼돌|12억",
        "yoon_visit": "금고|재방문",
        "sera_draft": "초안|훔|서류",
        "cha_identity": "친자|친아들|사진|어머니",
        "seo_forgery": "위작|진품|판매|팔았",
        "seo_burn": "소각|벽난로|태웠|일기",
    }
    admissions = catalog.testimony["admissionEntries"]
    own_flags = set()
    for rule in catalog.findings:
        if rule["suspectId"] == suspect:
            own_flags.add(rule["flag"])
    for flag, pattern in flag_patterns.items():
        if (
            flag in flags
            and flag in own_flags
            and re.search(pattern, question)
            and flag in admissions
        ):
            return [deepcopy(admissions[flag])]
    selectors = [
        ("snoring", "코.*고|22:25"),
        ("missing-draft", "초안|봉투|분실"),
        ("dining", "식당|위스키"),
        ("white-glove", "흰.*장갑|22:40"),
        ("knock", "노크|22:50"),
        ("crying", "백세라|울"),
        ("absence", "화장실|거실|35"),
        ("fireplace", "벽난로|뒷모습|태웠"),
        ("breathing", "호흡|숨|살아"),
        ("room", "어디|방.*있"),
        ("meeting", "면담|언제|몇.*시|와인|혈압"),
    ]
    for key, pattern in selectors:
        match = next((entry for entry in movement_entries if entry["key"] == key), None)
        if match and re.search(pattern, question):
            return [match]
    person = catalog.people[suspect]
    if re.search(r"누구|직업|몇.*살|나이|자기소개", question):
        return [
            {
                "key": "profile",
                "title": person["name"] + "의 자기소개",
                "text": person["statement"],
                "nature": "본인 진술",
            }
        ]
    return []
