"""공개 카탈로그의 응답 키와 자료 구조를 정의한다."""

from typing import TypedDict


class PublicCatalog(TypedDict):
    """소개 화면과 수사 시작 화면에서 읽는 공개 카탈로그를 정의한다.

    Args:
        없음.

    Returns:
        PublicCatalog: 사건과 인물의 공개 정보 및 화면 설정을 담은 사전.
    """

    caseId: str
    scenarioVersion: str
    case: dict
    motiveOptions: list
    methodOptions: list
    publicTimeline: list
    characters: list[dict]
    questionLimit: int
    briefing: list[dict[str, str]]
    openingVideo: str
    application: dict
    display: dict
    screenLabels: dict[str, str]
