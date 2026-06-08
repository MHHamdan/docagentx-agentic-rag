from typing import Any

MIN_CITATION_SCORE = 0.60
HIGH_CONFIDENCE_SCORE = 0.75
MEDIUM_CONFIDENCE_SCORE = 0.60


def verify_retrieved_citations(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {
            "status": "no_evidence",
            "verified": False,
            "message": "No retrieved chunks were available to support the answer.",
            "verified_citation_count": 0,
            "total_citation_count": 0,
            "min_score_required": MIN_CITATION_SCORE,
        }

    verified_citations = []

    for result in results:
        has_required_fields = all(
            result.get(field) is not None
            for field in ["chunk_id", "page_number", "chunk_index", "score", "text"]
        )

        score_is_acceptable = float(result.get("score", 0)) >= MIN_CITATION_SCORE
        text_is_not_empty = bool(str(result.get("text", "")).strip())

        if has_required_fields and score_is_acceptable and text_is_not_empty:
            verified_citations.append(result["chunk_id"])

    verified = len(verified_citations) > 0

    return {
        "status": "verified" if verified else "low_confidence",
        "verified": verified,
        "message": (
            "At least one retrieved citation passed verification."
            if verified
            else "Retrieved citations did not meet the minimum verification threshold."
        ),
        "verified_citation_count": len(verified_citations),
        "total_citation_count": len(results),
        "verified_chunk_ids": verified_citations,
        "min_score_required": MIN_CITATION_SCORE,
    }


def estimate_answer_confidence(results: list[dict[str, Any]]) -> dict[str, Any]:
    if not results:
        return {
            "level": "none",
            "score": 0.0,
            "reason": "No retrieved evidence was available.",
        }

    scores = [float(result.get("score", 0)) for result in results]
    average_score = sum(scores) / len(scores)

    if average_score >= HIGH_CONFIDENCE_SCORE:
        level = "high"
    elif average_score >= MEDIUM_CONFIDENCE_SCORE:
        level = "medium"
    else:
        level = "low"

    return {
        "level": level,
        "score": round(average_score, 4),
        "reason": f"Confidence is based on the average retrieval score of {len(results)} chunks.",
    }
