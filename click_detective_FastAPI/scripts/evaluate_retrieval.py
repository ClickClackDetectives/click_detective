"""대사 모델을 실행하지 않고 공개 동선 진술의 검색 품질을 비교한다."""

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from app.dialogue.preprocess_agent.free_questions import movement
from app.dialogue.text_relevance import text_relevance

from .retrieval_metrics import calibrate, measure, summarize

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = Path(__file__).with_name("retrieval_eval_cases.json")


def load_cases(dataset_path, data_dir):
    """평가 문항과 각 문항에서 공개 가능한 진술을 준비한다.

    Args:
        dataset_path: 질문, 기대 진술 ID, 공개 상태를 지정한 JSON.
        data_dir: FastAPI 데이터 루트.
    Returns:
        tuple: 문항별 평가 데이터와 검색용 진술 목록.
    """
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    case_dir = data_dir / "case"
    case_data = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    if (
        dataset["schema_version"] != 1
        or dataset["scope"] != "public_movement"
        or dataset["case_id"] != case_data["caseId"]
    ):
        raise ValueError("Dataset schema, scope or case ID does not match.")
    source = json.loads(
        (case_dir / "testimony-templates.private.json").read_text(encoding="utf-8")
    )
    catalog = SimpleNamespace(
        statement_people={
            person["suspectId"]: person for person in source["characters"]
        }
    )
    cases, documents = [], {}
    group_ids = set()
    for group in dataset["groups"]:
        group_id, split = group["id"], group["split"]
        suspect = group["suspect_id"]
        flags = group.get("revealed_flags", [])
        if group_id in group_ids or split not in {"calibration", "test"}:
            raise ValueError(f"Duplicate group or invalid split: {group_id}")
        group_ids.add(group_id)
        entries = movement(catalog, suspect, flags)
        corpus = {
            f"{suspect}-{e['key']}": (
                e["key"],
                f"{e.get('time') or ''} {e['title']} {e['text']}".strip(),
            )
            for e in entries
        }
        gold = group["expected_fact_ids"]
        if len(gold) != len(set(gold)) or set(gold) - corpus.keys():
            raise ValueError(
                f"Expected fact is not available for this case: {group_id}"
            )
        for number, question in enumerate(group["questions"], 1):
            case_id = f"{group_id}-{number}"
            cases.append(
                {
                    "id": case_id,
                    "split": split,
                    "group": group_id,
                    "suspect_id": suspect,
                    "revealed_flags": flags,
                    "expected_fact_ids": gold,
                    "kind": question["kind"],
                    "question": question["text"],
                }
            )
            documents[case_id] = corpus
    if not any(case["split"] == "test" for case in cases):
        raise ValueError("Dataset has no held-out test questions.")
    return cases, documents


def lexical_rankings(cases, documents):
    """현재 브랜치의 단어·문자 점수로 모든 공개 후보에 순위를 매긴다.

    Args:
        cases: 평가 질문 목록.
        documents: 문항별 공개 후보의 ID, 짧은 키와 검색용 원문.
    Returns:
        dict: 문항 ID별로 정렬된 (진술 ID, 점수).
    """
    return {
        case["id"]: sorted(
            (
                (fact_id, text_relevance(case["question"], key, text))
                for fact_id, (key, text) in documents[case["id"]].items()
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )
        for case in cases
    }


def dense_rankings(cases, documents, args):
    """정규화된 질문·진술 임베딩의 내적으로 코사인 유사도를 계산한다.

    Args:
        cases: 평가 질문 목록.
        documents: 문항별 공개 후보의 ID, 짧은 키와 검색용 원문.
        args: 임베딩 모델, 실행 장치, 선택적 질의·문서 접두어를 담은 설정.
    Returns:
        dict: 문항 ID별로 정렬된 (진술 ID, 코사인 유사도).
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        raise SystemExit("Dense evaluation requires sentence-transformers.") from error

    model = SentenceTransformer(args.embedding_model, device=args.device)
    passages = list(
        dict.fromkeys(
            text for corpus in documents.values() for _, text in corpus.values()
        )
    )
    passage_vectors = model.encode_document(
        passages, prompt=args.passage_prefix, normalize_embeddings=True
    )
    vectors = dict(zip(passages, passage_vectors, strict=True))
    question_vectors = model.encode_query(
        [case["question"] for case in cases],
        prompt=args.query_prefix,
        normalize_embeddings=True,
    )
    return {
        case["id"]: sorted(
            (
                (fact_id, float(question_vector @ vectors[text]))
                for fact_id, (_, text) in documents[case["id"]].items()
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )
        for case, question_vector in zip(cases, question_vectors, strict=True)
    }


def evaluate(cases, rankings, top_k):
    """기준 조정과 최종 평가를 분리하고 질문 유형별 결과를 만든다.

    Args:
        cases: 기준 조정과 최종 평가 문항.
        rankings: 모든 문항의 후보 점수.
        top_k: 점수 기준 통과 후 반환할 진술 수 상한.
    Returns:
        dict: 점수 기준, 전체 지표와 질문 유형·개별 문항 결과.
    """
    calibration = [case for case in cases if case["split"] == "calibration"]
    test = [case for case in cases if case["split"] == "test"]
    threshold = calibrate(calibration, rankings, top_k)
    test_rows = measure(test, rankings, top_k, threshold)
    return {
        "minimum_score": threshold,
        "calibration": summarize(measure(calibration, rankings, top_k, threshold)),
        "test": summarize(test_rows),
        "test_by_kind": {
            kind: summarize([row for row in test_rows if row["kind"] == kind])
            for kind in sorted({row["kind"] for row in test_rows})
        },
        "test_rows": test_rows,
    }


def main():
    """검색 기준선과 선택한 임베딩 모델의 비교를 실행한다.

    Args:
        없음.
    Returns:
        None: 요약을 표준 출력에 쓰고 선택적으로 전체 JSON 보고서를 저장한다.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--embedding-model", help="Sentence Transformers 모델 ID 또는 경로"
    )
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--query-prefix")
    parser.add_argument("--passage-prefix")
    parser.add_argument("--output", type=Path, help="전체 JSON 보고서 파일 경로")
    args = parser.parse_args()
    if args.top_k < 1:
        parser.error("--top-k must be at least 1")

    cases, documents = load_cases(args.dataset, args.data_dir)
    rankings = {"lexical": lexical_rankings(cases, documents)}
    if args.embedding_model:
        rankings["dense"] = dense_rankings(cases, documents, args)
    report = {
        "top_k": args.top_k,
        "embedding": (
            {
                "model": args.embedding_model,
                "device": args.device,
                "query_prefix": args.query_prefix,
                "passage_prefix": args.passage_prefix,
            }
            if args.embedding_model
            else None
        ),
        "backends": {
            backend: evaluate(cases, ranked, args.top_k)
            for backend, ranked in rankings.items()
        },
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    summary = {
        "top_k": args.top_k,
        "embedding": report["embedding"],
        "backends": {
            backend: {key: value for key, value in result.items() if key != "test_rows"}
            for backend, result in report["backends"].items()
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
