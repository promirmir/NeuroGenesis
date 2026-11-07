"""Optional GPU-ready foundation brain: trainable ordered-byte predictive cortex.

This is a REAL learned PyTorch neural network, independent of external LLMs.
It uses fused GRU cortical dynamics, two temporal timescales, a next-byte
objective and a latent predictive objective. No network activity, no implicit
data downloads, no pretrained weights and no subjective-awareness claim.

This module is deliberately optional: the existing small Windows EXE and
schema-1 SQLite neural memory remain intact when PyTorch is not installed.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import os
from pathlib import Path
import tempfile
from typing import Any

try:
    import torch
    from torch import nn
    from torch.nn import functional as F
except ImportError:  # Standard v0.5.6 app must not require heavyweight torch.
    torch = None
    nn = None
    F = None


@dataclass(frozen=True)
class FoundationConfig:
    """User-bounded architecture; larger sizes require actual resources."""

    vocab_size: int = 256
    hidden_size: int = 256
    fast_layers: int = 4
    slow_layers: int = 1
    chunk_size: int = 32
    max_sequence: int = 512
    latent_weight: float = 0.10
    dropout: float = 0.0
    parameter_limit: int = 50_000_000

    def __post_init__(self) -> None:
        for field in ("vocab_size", "hidden_size", "fast_layers",
                      "slow_layers", "chunk_size", "max_sequence",
                      "parameter_limit"):
            value = getattr(self, field)
            if type(value) is not int or value <= 0:
                raise ValueError("invalid integer configuration: " + field)
        if not (self.vocab_size == 256 and 16 <= self.hidden_size <= 2048
                and 1 <= self.fast_layers <= 24
                and 1 <= self.slow_layers <= 8
                and 2 <= self.chunk_size <= self.max_sequence <= 4096
                and 10_000 <= self.parameter_limit <= 2_000_000_000):
            raise ValueError("foundation architecture violates resource bounds")
        if (type(self.latent_weight) not in (int, float)
                or not math.isfinite(self.latent_weight)
                or not 0 <= self.latent_weight <= 1):
            raise ValueError("invalid latent learning weight")
        if (type(self.dropout) not in (int, float)
                or not math.isfinite(self.dropout)
                or not 0 <= self.dropout < 0.5):
            raise ValueError("invalid dropout")


@dataclass
class FoundationOutput:
    """Causal logits and losses, NOT proof of semantic understanding."""

    logits: Any
    loss: Any
    token_loss: Any
    latent_loss: Any


class FoundationBrain(nn.Module if nn is not None else object):
    """Trainable multi-timescale predictive neural brain.

    Fast GRU sees ordered bytes causally. Slow GRU summarizes completed chunks.
    The slow contextual vector for any position comes ONLY from an earlier
    chunk, so no future token leaks into a prediction. Tokens in the same
    chunk use the fast recurrent pathway for their history.

    Autonomy is in the learned weights and hidden dynamics, NOT in externally
    supplied scripted Q/A associations. This remains a research prototype.
    """

    CHECKPOINT_VERSION = 1
    MAX_CHECKPOINT_BYTES = 2 * 1024 * 1024 * 1024

    def __init__(self, config: FoundationConfig | None = None) -> None:
        if nn is None:
            raise RuntimeError("FoundationBrain requires the optional PyTorch foundation dependency")
        super().__init__()
        cfg = config or FoundationConfig()
        if type(cfg) is not FoundationConfig:
            raise TypeError("config must be FoundationConfig")
        self.config = cfg
        d = cfg.hidden_size
        self.embedding = nn.Embedding(cfg.vocab_size, d)
        self.fast_cortex = nn.GRU(
            d, d, num_layers=cfg.fast_layers, batch_first=True,
            dropout=cfg.dropout if cfg.fast_layers > 1 else 0.0)
        self.slow_cortex = nn.GRU(
            d, d, num_layers=cfg.slow_layers, batch_first=True,
            dropout=cfg.dropout if cfg.slow_layers > 1 else 0.0)
        self.context_norm = nn.LayerNorm(2 * d)
        self.symbol_head = nn.Linear(2 * d, cfg.vocab_size)
        self.latent_predictor = nn.Linear(2 * d, d)
        count = self.parameter_count
        if count > cfg.parameter_limit:
            raise ValueError(
                f"foundation model has {count} parameters, above operator limit "
                f"{cfg.parameter_limit}")

    @property
    def parameter_count(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def _check_tokens(self, tokens: Any) -> None:
        if not torch.is_tensor(tokens) or tokens.dtype != torch.long:
            raise ValueError("tokens must be a torch.long tensor")
        if tokens.ndim != 2:
            raise ValueError("tokens must have [batch, time] dimensions")
        batch, timesteps = tokens.shape
        if not 1 <= batch <= 128 or not 2 <= timesteps <= self.config.max_sequence:
            raise ValueError("token batch or sequence exceeds configured bounds")
        if not torch.all((tokens >= 0) & (tokens < self.config.vocab_size)).item():
            raise ValueError("out-of-range byte token")

    def forward(self, tokens: Any) -> FoundationOutput:
        """Compute causal next-byte and next-latent predictive losses.

        This is self-supervised learning: target is next observed byte.
        No teacher text answers or network access are involved.
        """
        self._check_tokens(tokens)
        batch, length = tokens.shape
        d = self.config.hidden_size
        embedded = self.embedding(tokens)
        fast, _ = self.fast_cortex(embedded)

        # Inference and training share identical causal chunk boundaries.
        # A chunk's summary is never visible to positions in that chunk.
        spans = [fast[:, start:min(start + self.config.chunk_size, length), :].mean(dim=1)
                 for start in range(0, length, self.config.chunk_size)]
        summaries = torch.stack(spans, dim=1)
        slow, _ = self.slow_cortex(summaries)
        previous = torch.cat((slow.new_zeros(batch, 1, d), slow[:, :-1, :]), dim=1)
        context = torch.repeat_interleave(
            previous, repeats=self.config.chunk_size, dim=1)[:, :length, :]
        representation = self.context_norm(torch.cat((fast, context), dim=-1))
        logits = self.symbol_head(representation)

        ce_loss = F.cross_entropy(
            logits[:, :-1, :].contiguous().view(-1, self.config.vocab_size),
            tokens[:, 1:].contiguous().view(-1))
        latent_forecast = self.latent_predictor(representation[:, :-1, :])
        latent_target = fast[:, 1:, :].detach()
        predictive_loss = F.mse_loss(latent_forecast, latent_target)
        loss = ce_loss + self.config.latent_weight * predictive_loss
        return FoundationOutput(logits, loss, ce_loss, predictive_loss)

    def train_batch(self, tokens: Any, optimizer: Any, *,
                    gradient_clip: float = 1.0) -> dict[str, float]:
        if (type(gradient_clip) not in (int, float)
                or not math.isfinite(gradient_clip)
                or not 0 < gradient_clip <= 10):
            raise ValueError("invalid gradient clip")
        self.train()
        optimizer.zero_grad(set_to_none=True)
        out = self(tokens)
        if not bool(torch.isfinite(out.loss).item()):
            raise ValueError("non-finite foundation training loss")
        out.loss.backward()
        norm = nn.utils.clip_grad_norm_(self.parameters(), gradient_clip,
                                        error_if_nonfinite=True)
        optimizer.step()
        return {
            "loss": float(out.loss.detach().cpu()),
            "next_byte_ce": float(out.token_loss.detach().cpu()),
            "latent_prediction_mse": float(out.latent_loss.detach().cpu()),
            "gradient_norm": float(norm.detach().cpu()),
        }

    def statistics(self) -> dict[str, Any]:
        return {
            "parameters": self.parameter_count,
            "hidden_size": self.config.hidden_size,
            "fast_layers": self.config.fast_layers,
            "slow_layers": self.config.slow_layers,
            "chunk_size": self.config.chunk_size,
            "device": str(next(self.parameters()).device),
            "trained_data_provenance": "not recorded in weights",
            "model_kind": "multiscale_recurrent_self_supervised_foundation",
        }

    def save_checkpoint(self, path: str | Path, *,
                        training_steps: int = 0) -> None:
        """Save a versioned, atomic *numerical* state, without raw training text."""
        if type(training_steps) is not int or training_steps < 0:
            raise ValueError("invalid training step counter")
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "version": self.CHECKPOINT_VERSION,
            "config": asdict(self.config),
            "training_steps": training_steps,
            "parameters": {
                k: v.detach().cpu().clone()
                for k, v in self.state_dict().items()
            },
        }
        name = None
        try:
            with tempfile.NamedTemporaryFile(
                    prefix=".foundation-", suffix=".tmp",
                    dir=dest.parent, delete=False) as handle:
                name = handle.name
                torch.save(state, handle)
                handle.flush()
                os.fsync(handle.fileno())
            if Path(name).stat().st_size > self.MAX_CHECKPOINT_BYTES:
                raise ValueError("foundation checkpoint exceeds size bound")
            os.replace(name, dest)
        finally:
            if name is not None and Path(name).exists():
                os.unlink(name)

    @classmethod
    def load_checkpoint(cls, path: str | Path, *,
                        device: str = "cpu") -> tuple[FoundationBrain, int]:
        if torch is None:
            raise RuntimeError("PyTorch is required to load foundation weights")
        path = Path(path)
        if path.stat().st_size > cls.MAX_CHECKPOINT_BYTES:
            raise ValueError("checkpoint exceeds size bound")
        # weights_only rejects arbitrary pickle objects. Still accept only
        # operator-trusted checkpoints; untrusted files are not an API.
        state = torch.load(path, map_location="cpu", weights_only=True)
        if (type(state) is not dict
                or state.get("version") != cls.CHECKPOINT_VERSION
                or type(state.get("config")) is not dict
                or type(state.get("training_steps")) is not int
                or state["training_steps"] < 0):
            raise ValueError("invalid foundation checkpoint")
        cfg = FoundationConfig(**state["config"])
        model = cls(cfg)
        model.load_state_dict(state["parameters"], strict=True)
        if any(not bool(torch.isfinite(t).all().item())
               for t in model.state_dict().values()):
            raise ValueError("non-finite foundation parameters")
        model.to(device)
        return model, state["training_steps"]


def encode_utf8(text: str) -> list[int]:
    """Ordered UTF-8 tokens; no 8-bin hash, no fabricated word semantics."""
    if type(text) is not str:
        raise TypeError("text must be str")
    data = text.encode("utf-8")
    if not data:
        raise ValueError("cannot encode empty text")
    return list(data)
