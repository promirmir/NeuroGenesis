"""Conservative, session-only lexical topic carryover for sourced follow-ups.

This is NOT a language model, semantic coreference or cross-session memory.
Only explicit 'A ...?' / 'I ...?' follow-ups with fresh substantive terms
qualify; the source URL and new terms must match a retained passage.
"""
from __future__ import annotations

from dataclasses import dataclass

from .knowledge import MAX_QUERY_CHARS, _terms

# Question scaffolding is not evidence of a new factual requirement. Keep
# query nouns/predicates, not "gdzie" or "jego", as mandatory focus terms.
FILLERS = frozenset((
    "co", "czym", "czy", "jak", "jaki", "jaka", "jakie", "jaką", "jakim",
    "gdzie", "kiedy", "dlaczego", "który", "która", "które", "kto",
    "jego", "jej", "ich", "temat", "temacie", "więcej", "dalej",
    "teraz", "tego", "tym", "tam", "też", "jeszcze", "powiedz",
    "opis", "opisz", "podaj", "informacje", "informacji", "sprawie",
))


@dataclass(frozen=True)
class FollowUp:
    query: str
    mandatory_focus_terms: tuple[str, ...]


def expand_followup(message: str, previous_question: str) -> FollowUp | None:
    """Only explicit short follow-up syntax; no guess on missing new detail.

    The returned query never changes the user's stored observation (only the
    ephemeral retrieval terms) and is still subject to the regular evidence
    overlap/abstention checks. It does NOT mean the answer is understood.
    """
    if (type(message) is not str or type(previous_question) is not str
            or not 1 <= len(message) <= 220
            or not 1 <= len(previous_question) <= MAX_QUERY_CHARS):
        return None
    current = " ".join(message.casefold().split())
    if not current.endswith("?") or not current.startswith(("a ", "i ", "oraz ")):
        return None
    focus = tuple(t for t in _terms(message) if t not in FILLERS)[:4]
    anchor = tuple(t for t in _terms(previous_question) if t not in FILLERS)[:5]
    if not focus or not anchor:
        return None
    query = " ".join((*focus, *anchor))
    if len(query) > MAX_QUERY_CHARS:
        return None
    return FollowUp(query=query, mandatory_focus_terms=focus)
