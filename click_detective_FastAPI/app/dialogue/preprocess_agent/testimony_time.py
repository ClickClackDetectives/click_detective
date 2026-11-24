"""벡터 검색 결과에서 명시한 시각과 모순되는 기록을 제외한다."""

import re

NATIVE_HOURS = {
    word: index
    for index, word in enumerate(
        "한 두 세 네 다섯 여섯 일곱 여덟 아홉 열 열한 열두".split(), 1
    )
}
SINO = {word: index for index, word in enumerate("영일이삼사오육칠팔구")}
CLOCK = re.compile(
    r"(?<![0-9])(?P<colon_hour>[0-9]{1,2}):(?P<colon_minute>[0-9]{2})(?![0-9])"
    r"|(?<![가-힣0-9])(?P<named>정오|자정)"
    r"|(?<![가-힣0-9])(?P<period>오후|오전|새벽|저녁|밤)?\s*"
    r"(?P<hour>[0-9]{1,2}|열\s*[한두]|[영일이삼사오육칠팔구십]{1,3}|"
    r"한|두|세|네|다섯|여섯|일곱|여덟|아홉|열)\s*시\s*"
    r"(?:(?P<half>반)|(?P<minute>[0-9]{1,2}|[영일이삼사오육칠팔구십]{1,3})\s*분)"
)
IMPRECISE_SUFFIX = re.compile(
    r"^\s*(?:에\s*)?(?:쯤|즈음|무렵|전후|부터|까지|이전|이후|직전|직후|앞서|"
    r"경(?=$|[에쯤\s,.!?])|(?:좀|조금)\s*(?:전|뒤|후|지나)|"
    r"[전후뒤](?=$|[에\s,.!?]))"
)


def korean_number(text):
    """시와 분에 쓰인 숫자를 읽는다.

    Args:
        text: 아라비아 숫자 또는 한글 수 표현.
    Returns:
        int | None: 해석할 수 있는 숫자.
    """
    text = "".join(text.split())
    if text.isascii() and text.isdigit():
        return int(text)
    if text in NATIVE_HOURS:
        return NATIVE_HOURS[text]
    if text in SINO:
        return SINO[text]
    if text.count("십") == 1:
        tens, units = text.split("십")
        digits = {"": 0, **SINO}
        if tens in digits and units in digits:
            return 10 * (SINO[tens] if tens else 1) + digits[units]
    return None


def exact_minute(question):
    """단일한 정확한 시각만 후처리 조건으로 변환한다.

    Args:
        question: 질문 원문.
    Returns:
        int | None: 자정 기준 분. 범위·근사·모호한 시간은 None.
    """
    matches = list(CLOCK.finditer(question))
    if len(matches) != 1:
        return None
    match = matches[0]
    fields = match.groupdict()
    if IMPRECISE_SUFFIX.search(question[match.end() :]) or re.search(
        r"(?<![가-힣])(?:약|대략)\s*$", question[: match.start()]
    ):
        return None
    if fields["colon_hour"]:
        hours, minutes = int(fields["colon_hour"]), int(fields["colon_minute"])
    elif fields["named"]:
        hours, minutes = (12 if fields["named"] == "정오" else 0), 0
    else:
        hours = korean_number(fields["hour"])
        minutes = 30 if fields["half"] else korean_number(fields["minute"])
        if hours is None or minutes is None:
            return None
        period = fields["period"]
        if period and not 1 <= hours <= 12:
            return None
        if period in {"오후", "저녁", "밤"}:
            hours = 0 if period == "밤" and hours == 12 else hours % 12 + 12
        elif period in {"오전", "새벽"}:
            hours %= 12
        elif 1 <= hours <= 12:
            return None
    if not (0 <= hours < 24 and 0 <= minutes < 60):
        return None
    return hours * 60 + minutes


def fits_time(candidate, minute):
    """시간이 확인된 개별 진술과 질문에 적힌 시각을 비교한다.

    Args:
        candidate: E5가 평가한 개별 진술 또는 동선 묶음.
        minute: 질문에 적힌 자정 기준 분.
    Returns:
        bool: 시간 정보가 없거나 기록에 해당 시각이 포함되는지 여부.
    """
    if candidate.topic:
        return False
    entry = candidate.entries[0]
    if entry.get("start") is None:
        return True
    start = entry["start"] % 1440
    end = entry.get("end", entry["start"]) % 1440
    if end < start:
        return minute >= start or minute <= end
    return start <= minute <= end
