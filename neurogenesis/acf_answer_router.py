"""Optional, real ACF-mediated *local* retrieval for the bundled Qwen.

The live ACF snapshot predicts a next semantic category from PRIOR
observations. A candidate source can enter an actual Qwen answer only if:
- ACF prequential error beats fixed, persistence and constant controls;
- the independent *current question* is tagged with that same category by
  the genuine local Qwen classifier (no forecast as asserted knowledge);
- approved local TXT contains a candidate with >=2 distinct literal
  query anchors, absent from baseline question-only retrieval.

This is an experimental routing decision, NOT proven task improvement.
Default dialogue and autonomous goal generation never enable this path.
No files/network are changed, no private question or passages are logged.
"""
from __future__ import annotations

from pathlib import Path
import re
import sqlite3
from typing import Any, Callable

from .acf import AdaptiveCognitiveFabric
from .acf_semantics import AXES, VERSION, MAX_SOURCE_CHARS
from .local_knowledge import LocalKnowledge
from .semantic_policy import QUERIES, decide

# Do not count generic Polish/English task words as evidence relevance.
_STOP = frozenset("""
jak jakie która który które czy dla jest albo oraz lub przez gdzie kiedy
co czym czymś czymś ze ten tego temu tego tych ich oni nasze można proszę
opis opisz wyjaśnij sprawdź znajdź napisz chcesz można dane dokument plik
tam źródło temat tekst rzeczy informacje znaczenie system użytkownik model
what how which where when with from about into that this could would does
give show explain information data files document source model system
""".split())
MIN_ANCHORS = 2
MAX_ADDED = 1


def _anchors(value: str) -> set[str]:
    return {word for word in re.findall(r"[^\W_]{4,}", value.casefold(),
                                        flags=re.UNICODE)
            if word not in _STOP}


def _report(status: str, *, axis: str | None = None, added: int = 0,
            scored: int = 0) -> dict[str, Any]:
    return {
        "status": status,
        "predicted_axis": axis,
        "added_approved_txt_passages": added,
        "prequential_scores": scored,
        "neural_task_improvement_proven": False,
        "current_question_verified_by_local_qwen": status in (
            "acf_passage_added", "no_new_question_grounded_source"),
        "local_read_only": True,
        "cloud_or_external_search": False,
    }


def route_for_question(
        question: str,
        baseline: list[dict[str, Any]],
        knowledge: LocalKnowledge,
        acf_state_path: str | Path,
        classify: Callable[[str], dict[str, Any]]
        ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return grounded, bounded sources and privacy-safe routing counters.

    Never use synthetic features or the ACF's forecast as a citation.
    On absent/corrupt state or classifier failure, preserve baseline RAG.
    """
    if (type(question) is not str or type(baseline) is not list
            or not isinstance(knowledge, LocalKnowledge)
            or not callable(classify)
            or not isinstance(acf_state_path, (str, Path))):
        raise ValueError("Invalid experimental ACF routing request.")
    if not question.strip() or len(question) > MAX_SOURCE_CHARS:
        return list(baseline), _report("question_outside_classifier_budget")
    path = Path(acf_state_path)
    if not path.is_file() or path.is_symlink():
        return list(baseline), _report("no_valid_acf_checkpoint")
    try:
        fabric = AdaptiveCognitiveFabric.load(path)
        decision = decide(fabric)
    except (OSError, ValueError, TypeError, KeyError, sqlite3.DatabaseError):
        return list(baseline), _report("invalid_acf_checkpoint")
    if decision.status != "eligible_for_local_prefetch":
        return list(baseline), _report(
            decision.status, scored=decision.scored_predictions)
    axis = decision.predicted_axis
    if axis not in QUERIES:
        return list(baseline), _report("unsupported_acf_axis")
    anchors = _anchors(question)
    if len(anchors) < MIN_ANCHORS:
        return list(baseline), _report("insufficient_question_anchors",
                                       axis=axis, scored=decision.scored_predictions)
    try:
        current = classify(question)
        if (type(current) is not dict or set(current) != {
                "axes", "version", "model", "inference",
                "cloud_api_used", "raw_text_persisted"}
                or current["version"] != VERSION
                or current["model"] != "Qwen3-1.7B-Q4_K_M"
                or current["inference"] != "actual_local_gguf_semantic_classification"
                or current["cloud_api_used"] is not False
                or current["raw_text_persisted"] is not False
                or type(current["axes"]) is not list
                or len(current["axes"]) != len(AXES)
                or any(type(x) not in (int, float) or x not in (0, 1)
                       for x in current["axes"])):
            return list(baseline), _report("invalid_current_semantics",
                                           scored=decision.scored_predictions)
        if current["axes"][AXES.index(axis)] != 1:
            return list(baseline), _report("predicted_topic_mismatch",
                                           axis=axis, scored=decision.scored_predictions)
        candidates = knowledge.retrieve(QUERIES[axis], limit=3)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError,
            TimeoutError, sqlite3.DatabaseError):
        return list(baseline), _report("local_semantics_or_retrieval_failed",
                                       scored=decision.scored_predictions)
    existing = {
        (str(row.get("file")), str(row.get("sha256")), str(row.get("text")))
        for row in baseline if type(row) is dict
    }
    matches = []
    for candidate in candidates:
        if type(candidate) is not dict:
            continue
        if (type(candidate.get("text")) is not str
                or type(candidate.get("file")) is not str
                or type(candidate.get("sha256")) is not str):
            continue
        key = (candidate["file"], candidate["sha256"], candidate["text"])
        if key in existing:
            continue
        overlap = len(_anchors(candidate["text"]) & anchors)
        if overlap >= MIN_ANCHORS:
            matches.append((overlap, candidate))
    if not matches:
        return list(baseline), _report(
            "no_new_question_grounded_source", axis=axis,
            scored=decision.scored_predictions)
    matches.sort(key=lambda p: -p[0])
    # Keep 3 baseline passages plus at most 1 ACF candidate to respect
    # contextual_messages()' existing 4-passage context budget.
    grounded = list(baseline[:3]) + [matches[0][1]]
    return grounded, _report(
        "acf_passage_added", axis=axis, added=MAX_ADDED,
        scored=decision.scored_predictions)
