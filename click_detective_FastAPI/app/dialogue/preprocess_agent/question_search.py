"""현재 수사에서 공개 가능한 진술을 질문 벡터로 검색한다."""

import asyncio
import logging
from dataclasses import dataclass, replace
from threading import Lock

from fastapi import HTTPException

from .free_questions import movement
from .planning import facts_from_entries
from .testimony_time import exact_minute, fits_time

logger = logging.getLogger(__name__)
OVERVIEW = (
    "그날 밤 무엇을 했나요? 어디에서 어떻게 시간을 보냈나요? "
    "사건 당일의 전체 동선과 알리바이를 시간 순서대로 설명해 주세요."
)
OFF_TOPIC = (
    "오늘 점심에 뭘 먹었나요? 평소 즐겨 먹는 음식은 무엇인가요? "
    "사건과 상관없는 일상이나 취미에 대한 질문입니다."
)
MAX_SCORE_GAP = 0.02


@dataclass(frozen=True)
class Candidate:
    """임베딩할 문장과 선택 시 공개할 진술을 연결한다.

    Args:
        text: E5로 검색할 진술 본문 또는 비교용 질문 표현.
        entries: 후보가 선택되면 공개할 원문. 사건 외 비교 문장은 빈 값.
        topic: 전체 동선처럼 묶음으로 반환하는 주제의 ID.
    Returns:
        Candidate: 게임 규칙으로 범위가 정해진 검색 후보.
    """

    text: str
    entries: tuple[dict, ...]
    topic: str | None = None


def public_candidates(catalog, suspect, flags):
    """공개 가능한 원문과 사건 외 질문을 판별할 비교 문장을 준비한다.

    Args:
        catalog: 사건 원문과 공개 규칙.
        suspect: 심문 중인 인물 ID.
        flags: 이미 공개한 쟁점 ID.
    Returns:
        list[Candidate]: 동선, 관계, 자기소개, 공개된 인정 진술과 비교 문장.
    """
    timeline = movement(catalog, suspect, flags)
    entries = {entry["key"]: entry for entry in timeline}
    admissions = catalog.testimony["admissionEntries"]
    for rule in catalog.findings:
        flag = rule["flag"]
        if rule["suspectId"] == suspect and flag in flags and flag in admissions:
            entry = admissions[flag]
            entries.setdefault(entry["key"], entry)
    for reply in catalog.statement_people[suspect]["relationshipReplies"]:
        for entry in reply["entries"]:
            entries.setdefault(entry["key"], {**entry, "_topic": reply["topicId"]})
    person = catalog.people[suspect]
    entries["profile"] = {
        "key": "profile",
        "title": person["name"] + "의 자기소개",
        "text": person["statement"],
        "nature": "본인 진술",
    }
    candidates = []
    for entry in entries.values():
        text = entry["text"]
        if "_topic" in entry:
            target = catalog.people[entry["_topic"].removeprefix("about-")]["name"]
            text = f"{target}에 대해 무엇을 알고 있나요? 어떤 사이인가요? {text}"
        elif entry["key"] == "profile":
            text = f"자기소개를 해 주세요. 어떤 일을 하나요? 직업은 무엇인가요? {text}"
        candidates.append(Candidate(text, (entry,)))
    if timeline:
        candidates.append(Candidate(OVERVIEW, tuple(timeline), "movement"))
    return [*candidates, Candidate(OFF_TOPIC, ())]


class QuestionSearch:
    """승인 후보를 E5 코사인 유사도로 정렬한다.

    Args:
        catalog: 현재 사건 카탈로그.
        settings: 검색 개수, 점수 하한과 장애 복구 설정.
        encoder: 질문과 진술을 단위 벡터로 인코딩하는 모델.
    Returns:
        QuestionSearch: 자유 질문의 승인 계획을 완성하는 객체.
    """

    def __init__(self, catalog, settings, encoder):
        """서버가 공유하는 모델과 진술 벡터 캐시를 준비한다.

        Args:
            catalog: 현재 사건 카탈로그.
            settings: 검색 및 복구 설정.
            encoder: 문장 임베딩을 계산하는 모델.
        Returns:
            None: 상태 초기화만 수행한다.
        """
        self.catalog = catalog
        self.settings = settings
        self.encoder = encoder
        self.passage_vectors = {}
        self.index_lock = Lock()

    def rank(self, question, candidates):
        """후보 원문의 벡터를 재사용하고 질문과의 유사도를 계산한다.

        Args:
            question: 플레이어가 입력한 원문.
            candidates: 현재 요청에 승인된 후보.
        Returns:
            list[tuple]: 점수가 높은 순서로 정렬한 (점수, 후보).
        """
        with self.index_lock:
            missing = list(
                dict.fromkeys(
                    candidate.text
                    for candidate in candidates
                    if candidate.text not in self.passage_vectors
                )
            )
            if missing:
                vectors = self.encoder.encode(missing, prefix="passage: ")
                self.passage_vectors.update(zip(missing, vectors, strict=True))
            passages = [
                self.passage_vectors[candidate.text] for candidate in candidates
            ]
        (query,) = self.encoder.encode([question], prefix="query: ")
        scored = [
            (float(query @ passage), candidate)
            for passage, candidate in zip(passages, candidates, strict=True)
        ]
        return sorted(scored, key=lambda item: item[0], reverse=True)

    async def refine(self, state, command, plan):
        """자유 질문의 원문과 검색 결과를 생성·기록 양쪽에 연결한다.

        Args:
            state: 현재 수사 상태.
            command: 플레이어의 심문 요청.
            plan: 검증된 명시 주제, 증거와 새 쟁점을 담은 승인 계획.
        Returns:
            ReplyPlan: 유사도 기준을 통과한 진술을 담은 계획.
        """
        if command.topic_id or plan.new_findings or not self.settings.rag_top_k:
            return plan
        candidates = public_candidates(self.catalog, plan.suspect_id, state["revealed"])
        try:
            async with asyncio.timeout(self.settings.timeout_seconds):
                ranked = await asyncio.to_thread(
                    self.rank, command.question, candidates
                )
        except (RuntimeError, TimeoutError, ValueError) as error:
            if not self.settings.fallback_on_error:
                status = 504 if isinstance(error, TimeoutError) else 502
                raise HTTPException(status, "Testimony vector search failed") from None
            logger.warning(
                "Testimony vector search recovered: %s", type(error).__name__
            )
            return plan

        minute = exact_minute(command.question)
        eligible = [
            (score, candidate)
            for score, candidate in ranked
            if minute is None or not candidate.entries or fits_time(candidate, minute)
        ]
        best, first = eligible[0]  # 사건 외 비교 문장은 시각과 관계없이 남는다.
        if best < self.settings.rag_min_score or not first.entries:
            return plan
        cutoff = max(self.settings.rag_min_score, best - MAX_SCORE_GAP)
        matches = [
            candidate
            for score, candidate in eligible
            if score >= cutoff and candidate.entries and not candidate.topic
        ][: self.settings.rag_top_k]
        selected = (
            list(first.entries)
            if first.topic
            else [entry for match in matches for entry in match.entries]
        )
        topics = {entry.get("_topic") for entry in selected}
        topic = first.topic or (topics.pop() if len(topics) == 1 else None)
        return replace(
            plan,
            topic=topic,
            entries=selected,
            facts=facts_from_entries(plan.suspect_id, selected),
        )
