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

from contextlib import closing
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


def validate_semantic_provenance(
        state_path: str | Path,
        fabric: AdaptiveCognitiveFabric) -> bool:
    """Require cursor correspondence to the *semantic* Qwen-tag ledger.

    Plain hashed sensory ACF snapshots must never become semantic decisions.
    Only schema/tagger identity is checked; this is not cryptographic proof
    that every row was genuinely emitted by a model.
    """
    path = Path(state_path)
    ledger = path.with_name("semantic_fabric.sqlite3")
    if (path.name != "semantic_fabric.acf.json"
            or not ledger.is_file() or ledger.is_symlink()
            or fabric.events <= 0 or fabric.last_event_id <= 0):
        return False
    try:
        uri = ledger.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, timeout=5)) as con:
            con.execute("PRAGMA query_only=ON")
            count, incompatible = con.execute(
                "SELECT COUNT(*), SUM(CASE WHEN tagger != ? THEN 1 ELSE 0 END) "
                "FROM observations WHERE id <= ?",
                (VERSION, fabric.last_event_id)).fetchone()
            final = con.execute(
                "SELECT id FROM observations WHERE id <= ? "
                "ORDER BY id DESC LIMIT 1", (fabric.last_event_id,)).fetchone()
        return (count == fabric.events and incompatible == 0
                and final is not None and final[0] == fabric.last_event_id)
    except (OSError, ValueError, sqlite3.DatabaseError):
        return False




def verified_current_axes(classified: dict[str, Any]) -> frozenset[str] | None:
    """Attested local Qwen topic *tags*, never factual verification."""
    if (type(classified) is not dict or set(classified) != {
            "axes", "version", "model", "inference",
            "cloud_api_used", "raw_text_persisted"}
            or classified["version"] != VERSION
            or classified["model"] != "Qwen3-1.7B-Q4_K_M"
            or classified["inference"] != "actual_local_gguf_semantic_classification"
            or classified["cloud_api_used"] is not False
            or classified["raw_text_persisted"] is not False
            or type(classified["axes"]) is not list
            or len(classified["axes"]) != len(AXES)
            or any(type(x) not in (int, float) or x not in (0, 1)
                   for x in classified["axes"])):
        return None
    return frozenset(axis for axis, value in zip(AXES, classified["axes"])
                     if value == 1)


def _select_candidate(
        question: str, baseline: list[dict[str, Any]],
        knowledge: LocalKnowledge, axis: str
        ) -> tuple[list[dict[str, Any]], bool]:
    """One identical approved-TXT search and context budget for ACF/control.

    Replacing the existing fourth source must strictly improve the
    literal anchor overlap; a merely new source does not qualify.
    This is an intentionally conservative heuristic, not truth scoring.
    """
    if axis not in QUERIES:
        return list(baseline), False
    anchors = _anchors(question)
    if len(anchors) < MIN_ANCHORS:
        return list(baseline), False
    existing = {
        (str(row.get("file")), str(row.get("sha256")), str(row.get("text")))
        for row in baseline if type(row) is dict
    }
    candidates = knowledge.retrieve(QUERIES[axis], limit=3)
    matches: list[tuple[int, dict[str, Any]]] = []
    for candidate in candidates:
        if (type(candidate) is not dict
                or any(type(candidate.get(k)) is not str
                       for k in ("text", "file", "sha256"))):
            continue
        key = (candidate["file"], candidate["sha256"], candidate["text"])
        if key in existing:
            continue
        overlap = len(_anchors(candidate["text"]) & anchors)
        if overlap >= MIN_ANCHORS:
            matches.append((overlap, candidate))
    if not matches:
        return list(baseline), False
    matches.sort(key=lambda pair: -pair[0])
    # Four is the actual contextual_messages source budget.
    # ACF/control must not crowd out a stronger existing fourth passage.
    if len(baseline) >= 4:
        last = baseline[3]
        last_overlap = (len(_anchors(str(last.get("text", ""))) & anchors)
                        if type(last) is dict else 0)
        if matches[0][0] <= last_overlap:
            return list(baseline), False
    return list(baseline[:3]) + [matches[0][1]], True


def route_with_topic_control(
        question: str, baseline: list[dict[str, Any]],
        knowledge: LocalKnowledge,
        classify: Callable[[str], dict[str, Any]]
        ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Non-neural matched retrieval control for the ACF scientific ablation.

    Same actual Qwen topic classifier, approved corpus, FTS query dictionary,
    lexical relevance threshold, one-added-passage and four-source budget.
    No ACF checkpoint or neural predictions are consulted.
    """
    if (type(question) is not str or type(baseline) is not list
            or not isinstance(knowledge, LocalKnowledge)
            or not callable(classify)):
        raise ValueError("Invalid non-neural topic control request.")
    if not question.strip() or len(question) > MAX_SOURCE_CHARS:
        return list(baseline), _report("question_outside_classifier_budget")
    if len(_anchors(question)) < MIN_ANCHORS:
        return list(baseline), _report("insufficient_question_anchors")
    try:
        axes = verified_current_axes(classify(question))
        if axes is None:
            return list(baseline), _report("invalid_current_semantics")
        # Precommitted fixed order: exactly ONE topic-query for this arm;
        # do not cherry-pick an axis using the held-out answer.
        axis = next((a for a in AXES if a in QUERIES and a in axes), None)
        if axis is None:
            return list(baseline), _report("no_supported_current_topic")
        sources, added = _select_candidate(question, baseline, knowledge, axis)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError,
            TimeoutError, sqlite3.DatabaseError):
        return list(baseline), _report("control_classification_or_retrieval_failed")
    return sources, _report(
        "topic_control_passage_added" if added else "no_new_question_grounded_source",
        axis=axis, added=int(added))


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
        if not validate_semantic_provenance(path, fabric):
            return list(baseline), _report("missing_semantic_ledger_provenance")
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
        axes = verified_current_axes(classify(question))
        if axes is None:
            return list(baseline), _report("invalid_current_semantics",
                                           scored=decision.scored_predictions)
        if axis not in axes:
            return list(baseline), _report("predicted_topic_mismatch",
                                           axis=axis, scored=decision.scored_predictions)
        grounded, added = _select_candidate(question, baseline, knowledge, axis)
    except (OSError, ValueError, KeyError, TypeError, RuntimeError,
            TimeoutError, sqlite3.DatabaseError):
        return list(baseline), _report("local_semantics_or_retrieval_failed",
                                       scored=decision.scored_predictions)
    return grounded, _report(
        "acf_passage_added" if added else "no_new_question_grounded_source",
        axis=axis, added=int(added), scored=decision.scored_predictions)
