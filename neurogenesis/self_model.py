"""An auditable computational self-model; no claims of sentience."""

from __future__ import annotations

from typing import Any
from .brain import Brain
from .origin import origin_record


def inspect(brain: Brain) -> dict[str, Any]:
    """Describe only directly measurable state and currently absent capabilities."""
    return {
        "system": "NeuroGenesis",
        "origin": origin_record(),
        "kind": "experimental_spiking_neural_network",
        "observable_state": brain.stats(),
        "capabilities": {
            "neuron_spiking": True,
            "synaptic_plasticity": True,
            "structural_growth": brain.config.growth_enabled,
            "persistent_snapshots": True,
            "text_feature_encoding": True,
            "natural_language_understanding": False,
            "autonomous_web_browsing": False,
            "consciousness_verified": False,
            "origin_metadata_available": True,
            "authenticated_operator_controls": False,
        },
        "epistemic_note": (
            "This report describes program state, not subjective experience, "
            "self-awareness or general intelligence."
        ),
    }
