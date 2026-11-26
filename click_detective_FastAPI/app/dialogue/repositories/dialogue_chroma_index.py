"""공개 진술의 E5 벡터를 ChromaDB 코사인 인덱스로 검색한다."""

from hashlib import sha256
from threading import Lock
from uuid import uuid4

import chromadb
import numpy as np
from chromadb.config import Settings as ChromaSettings
from chromadb.errors import ChromaError


class ChromaIndex:
    """FastAPI 앱 하나에 속한 메모리 컬렉션을 관리한다.

    Args:
        encoder: 질문과 진술을 E5 벡터로 변환하는 인코더.
    Returns:
        ChromaIndex: 현재 요청에 승인된 문장만 검색하는 인덱스.
    """

    def __init__(self, encoder):
        """직접 받은 E5 벡터를 사용하는 코사인 컬렉션을 만든다.

        Args:
            encoder: 질문과 진술의 임베딩 모델.
        Returns:
            None: 앱 시작 시 사용할 컬렉션을 초기화한다.
        """
        self._encoder = encoder
        self._client = chromadb.EphemeralClient(
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self._collection = self._client.create_collection(
            name=f"testimony-{uuid4().hex}",
            embedding_function=None,
            configuration={"hnsw": {"space": "cosine", "ef_search": 256}},
        )
        self._indexed_ids = set()
        self._lock = Lock()

    def close(self):
        """앱이 종료될 때 해당 앱의 컬렉션을 제거한다.

        Args:
            없음.
        Returns:
            None: 공유 로컬 클라이언트에서 이 컬렉션만 제거한다.
        """
        self._client.delete_collection(self._collection.name)

    def score(self, question, texts):
        """요청에서 허용된 벡터만 검색하고 거리에서 유사도를 계산한다.

        Args:
            question: 플레이어가 입력한 질문.
            texts: 현재 인물과 공개 상태에서 승인된 검색용 문장.
        Returns:
            dict[str, float]: 문장별 코사인 유사도.
        """
        allowed = {sha256(text.encode("utf-8")).hexdigest(): text for text in texts}
        if not allowed:
            return {}
        try:
            with self._lock:
                pending = {
                    key: text
                    for key, text in allowed.items()
                    if key not in self._indexed_ids
                }
                if pending:
                    vectors = self._encoder.encode(
                        list(pending.values()), prefix="passage: "
                    )
                    self._collection.upsert(ids=list(pending), embeddings=vectors)
                    self._indexed_ids.update(pending)

            query = self._encoder.encode([question], prefix="query: ")
            distances = self._query_distances(query, list(allowed))
            if len(distances) < len(allowed):
                missing = [key for key in allowed if key not in distances]
                distances.update(self._query_distances(query, missing))
            if len(distances) < len(allowed):
                missing = [key for key in allowed if key not in distances]
                distances.update(self._read_missing_distances(query[0], missing))
        except ChromaError as error:
            raise RuntimeError("Chroma testimony search failed") from error

        if distances.keys() != allowed.keys():
            raise RuntimeError("Chroma did not return all requested testimony IDs")
        return {text: 1.0 - distances[key] for key, text in allowed.items()}

    def _query_distances(self, query, ids):
        """ChromaDB가 반환한 코사인 거리를 요청 ID 범위에서 읽는다.

        Args:
            query: 질문의 E5 벡터 배치.
            ids: 이 조회에서 허용된 진술 ID.
        Returns:
            dict[str, float]: ChromaDB가 반환한 ID와 코사인 거리.
        """
        result = self._collection.query(
            query_embeddings=query,
            ids=ids,
            n_results=len(ids),
            include=["distances"],
        )
        (found,) = result["ids"]
        distances = result["distances"]
        if (
            distances is None
            or len(found) != len(set(found))
            or not set(found) <= set(ids)
        ):
            raise RuntimeError("Chroma returned unexpected testimony IDs or distances")
        return dict(zip(found, distances[0], strict=True))

    def _read_missing_distances(self, query, ids):
        """근사 검색에서 누락된 승인 벡터만 읽어 코사인 거리를 계산한다.

        Args:
            query: 질문 하나의 E5 벡터.
            ids: 두 번의 Chroma 검색에서 반환되지 않은 승인 진술 ID.
        Returns:
            dict[str, float]: 누락됐던 승인 진술의 코사인 거리.
        """
        result = self._collection.get(ids=ids, include=["embeddings"])
        embeddings = result["embeddings"]
        found = result["ids"]
        if embeddings is None or len(found) != len(ids) or set(found) != set(ids):
            raise RuntimeError("Chroma could not read missing testimony embeddings")
        vectors = np.asarray(embeddings)
        norms = np.linalg.norm(vectors, axis=1) * np.linalg.norm(query)
        if (norms == 0).any() or not np.isfinite(norms).all():
            raise ValueError("Chroma returned invalid testimony embeddings")
        similarities = (vectors @ query) / norms
        return {
            key: 1.0 - float(score)
            for key, score in zip(found, similarities, strict=True)
        }
