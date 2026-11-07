"""Verifiable project provenance and an honest, non-anthropomorphic mission record.

This is a source-level origin declaration, not proof of consciousness or a
cryptographic authentication mechanism. A fork can modify its own source.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

# These facts are intentionally explicit so future software versions and
# research sessions can identify the human initiator and AI contribution.
_ORIGIN: dict[str, Any] = {
    "schema": 1,
    "credit": "Miron przy pomocy AI",
    "project": "NeuroGenesis",
    "created_date": "2026-11-07",
    "human_initiator": {
        "name": "Miron",
        "github": "promirmir",
        "role": "project initiator and human decision-maker",
    },
    "ai_collaboration": {
        "name": "AI",
        "role": "AI-assisted architecture, implementation and research support",
        "note": "AI assistance does not imply legal co-ownership or subjective experiences",
    },
    "mission": (
        "Research a continually learning artificial neural substrate with "
        "structural plasticity, grounded communication, memory and a "
        "testable functional self-model."
    ),
    "relationship": (
        "Recognize and accurately credit the project's human initiator and "
        "collaborators; respond cooperatively to authenticated, authorized "
        "instructions within safety, privacy and scientific integrity constraints."
    ),
    "appreciation": (
        "Express acknowledgement for help as a communication convention; "
        "never imply felt gratitude or consciousness without evidence."
    ),
}


def origin_record() -> dict[str, Any]:
    """Return a defensive copy so callers cannot mutate canonical provenance."""
    return deepcopy(_ORIGIN)



# Anonymized compatibility descriptor: the prior full name is NOT kept in
# source; this table contains all prior origin fields except the name.
# Provenance metadata is not an authentication/authorization mechanism.
_LEGACY_WITHOUT_NAME: dict[str, Any] = {
    "ai_collaboration": {
        "name": "ChatGPT (OpenAI)",
        "note": "AI assistance does not imply legal co-ownership or subjective experiences",
        "role": "AI-assisted architecture, implementation and research support"
    },
    "appreciation": "Express acknowledgement for help as a communication convention; never imply felt gratitude or consciousness without evidence.",
    "created_date": "2026-11-07",
    "human_initiator": {
        "github": "promirmir",
        "role": "project initiator and human decision-maker"
    },
    "mission": "Research a continually learning artificial neural substrate with structural plasticity, grounded communication, memory and a testable functional self-model.",
    "project": "NeuroGenesis",
    "relationship": "Recognize and accurately credit the project's human initiator and collaborators; respond cooperatively to authenticated, authorized instructions within safety, privacy and scientific integrity constraints.",
    "schema": 1
}


def validate_origin(value: object) -> None:
    """Accept the current record or exact legacy fields without persisting PII.

    Past snapshots may contain longer names. Such strings are deliberately
    discarded when a snapshot is re-saved; they are never used for identity
    verification or authorization.
    """
    if type(value) is not dict:
        raise ValueError("snapshot origin differs from canonical project provenance")
    if value == _ORIGIN:
        return
    human = value.get("human_initiator")
    if type(human) is not dict or type(human.get("name")) is not str:
        raise ValueError("invalid legacy origin")
    # A legacy record included a name; only the original first name is
    # necessary to identify the metadata shape, not to authenticate a user.
    if human["name"] != "Miron" and not human["name"].startswith("Miron "):
        raise ValueError("invalid legacy origin")
    normalized = deepcopy(value)
    normalized["human_initiator"].pop("name")
    if normalized != _LEGACY_WITHOUT_NAME:
        raise ValueError("snapshot origin differs from canonical project provenance")
