"""현재 수사에서 공개 가능한 진술을 질문 벡터로 검색한다."""

import asyncio
import logging
from dataclasses import dataclass, replace
from time import perf_counter

from fastapi import HTTPException

from app.dialogue.services.diagnostics.dialogue_diagnostics import trace_event
from app.dialogue.services.preprocess_agent.rag.dialogue_fact_selection import (
    select_ranked,
)
from app.investigation.dto.investigation_interrogation_plan_dto import ReplyPlan
from app.investigation.services.interrogation.investigation_free_questions import (
    movement,
)
from app.investigation.services.interrogation.investigation_interrogation_planner import (
    facts_from_entries,
)

logger = logging.getLogger(__name__)
OVERVIEW = (
    "그날 밤 무엇을 했나요? 어디에서 어떻게 시간을 보냈나요? "
    "사건 당일의 전체 동선과 알리바이를 시간 순서대로 설명해 주세요."
)
OFF_TOPIC = (
    "오늘 점심에 뭘 먹었나요? 평소 즐겨 먹는 음식은 무엇인가요? "
    "사건과 상관없는 일상이나 취미에 대한 질문입니다."
)


@dataclass(frozen=True)
class Candidate:
    """임베딩할 문장과 선택 시 공개할 진술을 연결한다.

    Args:
        text: 검색용 제목·시각·본문 또는 비교용 질문 표현.
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
        else:
            label = " ".join(
                part for part in (entry["title"], entry.get("time")) if part
            )
            text = f"{label}. {text}"
        candidates.append(Candidate(text, (entry,)))
    if timeline:
        candidates.append(Candidate(OVERVIEW, tuple(timeline), "movement"))
    return [*candidates, Candidate(OFF_TOPIC, ())]


class QuestionSearch:
    """ChromaDB 유사도와 Kiwi BM25 순위로 승인 진술을 고른다.

    Args:
        catalog: 현재 사건 카탈로그.
        settings: 검색 개수, 점수 하한과 장애 복구 설정.
        index: 현재 요청에 승인된 후보의 유사도를 반환하는 인덱스.
        reranker: 독립 BM25 검색과 순위 결합을 담당하는 검색기.
    Returns:
        QuestionSearch: 자유 질문의 승인 계획을 완성하는 객체.
    """

    def __init__(self, catalog, settings, index, reranker=None):
        """사건 데이터와 검색 인덱스를 연결한다.

        Args:
            catalog: 현재 사건 카탈로그.
            settings: 검색 및 복구 설정.
            index: 승인 후보의 유사도를 구하는 인덱스.
            reranker: 설정에 따라 적용할 BM25 재정렬기.
        Returns:
            None: 상태 초기화만 수행한다.
        """
        self.catalog = catalog
        self.settings = settings
        self.index = index
        self.reranker = reranker

    def rank(self, question, candidates):
        """유사도 점수를 승인 후보에 연결해 정렬한다.

        Args:
            question: 플레이어가 입력한 원문.
            candidates: 현재 요청에 승인된 후보.
        Returns:
            list[tuple]: 점수가 높은 순서로 정렬한 (점수, 후보).
        """
        scores = self.index.score(
            question, [candidate.text for candidate in candidates]
        )
        scored = [(scores[candidate.text], candidate) for candidate in candidates]
        return sorted(scored, key=lambda item: item[0], reverse=True)

    def _bm25_scores(self, question, candidates):
        """공개된 개별 진술을 E5와 별도로 평가한다.

        Args:
            question: 플레이어가 입력한 원문.
            candidates: 현재 용의자가 공개할 수 있는 검색 후보.
        Returns:
            dict: 개별 진술의 BM25 점수. 복구 시 빈 점수표.
        """
        if self.reranker is None:
            return {}
        documents = tuple(
            dict.fromkeys(
                hit.text for hit in candidates if hit.entries and not hit.topic
            )
        )
        try:
            return self.reranker.scores(question, documents)
        except (RuntimeError, ValueError) as error:
            if not self.settings.fallback_on_error:
                raise
            logger.warning("Kiwi BM25 search recovered: %s", type(error).__name__)
            return {}

    async def _select_parallel(self, question, suspect, flags):
        """두 검색을 동시에 실행하고 최종 진술을 고른다.

        Args:
            question: 플레이어가 입력한 원문.
            suspect: 심문 중인 인물 ID.
            flags: 현재 수사에서 이미 공개된 쟁점 ID.
        Returns:
            tuple | None: 최종 진술과 주제 또는 매칭 없음.
        """
        if self.reranker is None:
            return await asyncio.to_thread(self.select, question, suspect, flags)
        candidates = public_candidates(self.catalog, suspect, flags)
        ranked, scores = await asyncio.gather(
            asyncio.to_thread(self.rank, question, candidates),
            asyncio.to_thread(self._bm25_scores, question, candidates),
        )
        return select_ranked(question, ranked, scores, self.settings, self.reranker)

    async def refine(self, plan, revealed) -> tuple[ReplyPlan, bool]:
        """자유 질문의 원문과 검색 결과를 생성·기록 양쪽에 연결한다.

        Args:
            plan: 검증된 명시 주제, 증거와 새 쟁점을 담은 승인 계획.
            revealed: 심문을 시작할 때 이미 공개된 쟁점 ID.
        Returns:
            tuple: 최종 승인 계획과 정상 검색에서 진술을 찾지 못했는지 여부.
        """
        if plan.topic or plan.new_findings or not self.settings.rag_top_k:
            return plan, False
        started = perf_counter()
        try:
            async with asyncio.timeout(self.settings.timeout_seconds):
                selected = await self._select_parallel(
                    plan.question, plan.suspect_id, revealed
                )
        except (RuntimeError, TimeoutError, ValueError) as error:
            if not self.settings.fallback_on_error:
                status = 504 if isinstance(error, TimeoutError) else 502
                raise HTTPException(status, "Testimony vector search failed") from None
            logger.warning(
                "Testimony vector search recovered: %s", type(error).__name__
            )
            return plan, False

        trace_event(
            "retrieval",
            elapsed_ms=round((perf_counter() - started) * 1000, 2),
            selected_count=len(selected[0]) if selected else 0,
        )
        if selected is None:
            return plan, True
        entries, topic = selected
        refined = replace(
            plan,
            topic=topic,
            entries=entries,
            facts=facts_from_entries(plan.suspect_id, entries),
        )
        return refined, False

    def select(self, question, suspect, flags):
        """공개 범위와 시각, 유사도 조건을 거쳐 최종 진술을 선택한다.

        Args:
            question: 플레이어가 입력한 원문.
            suspect: 심문 중인 인물 ID.
            flags: 현재 수사에서 이미 공개된 쟁점 ID.
        Returns:
            tuple | None: 최종 진술과 주제 또는 매칭 없음.
        """
        candidates = public_candidates(self.catalog, suspect, flags)
        ranked = self.rank(question, candidates)
        scores = self._bm25_scores(question, candidates)
        return select_ranked(question, ranked, scores, self.settings, self.reranker)
