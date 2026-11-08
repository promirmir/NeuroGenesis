"""Explicit, offline *experimental* generation from a trained Foundation checkpoint.

This is raw autoregressive next-byte prediction. Output can be malformed UTF-8
or meaningless; it is NOT a sourced answer, chat inference or verified fact.
No network, SQLite changes, automatic checkpoint promotion or model downloads.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
import threading
import time
from typing import Any

from .foundation import FoundationBrain, torch


def generate_candidate(checkpoint: str | Path, prompt: str, *,
                       trust_checkpoint: bool = False, max_new_bytes: int = 32,
                       device: str = "cpu",
                       cancel_event: threading.Event | None = None) -> dict[str, Any]:
    """Generate bounded, deterministic greedy continuation of a trusted local file.

    All model operations run in torch.no_grad(). This API does not touch the
    operator's persistent SQLite memory or move the candidate into chat.
    """
    if trust_checkpoint is not True:
        raise PermissionError("Explicitly confirm that this LOCAL checkpoint is trusted")
    if torch is None:
        raise RuntimeError("Optional PyTorch foundation dependency is required")
    if type(prompt) is not str or not prompt or len(prompt) > 512:
        raise ValueError("prompt must contain 1..512 characters")
    if type(max_new_bytes) is not int or not 1 <= max_new_bytes <= 64:
        raise ValueError("max_new_bytes must be in [1, 64]")
    if device not in ("cpu", "cuda"):
        raise ValueError("explicit CPU or CUDA selection required")
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA requested but not available")
    if cancel_event is not None and not isinstance(cancel_event, threading.Event):
        raise ValueError("cancel_event must be a threading.Event")
    path = Path(checkpoint)
    if path.suffix.lower() not in (".pt", ".pth") or not path.is_file() or path.is_symlink():
        raise ValueError("checkpoint must be an existing local regular .pt/.pth file")
    if cancel_event is not None and cancel_event.is_set():
        raise InterruptedError("candidate inference cancelled before loading")
    model, trained_steps = FoundationBrain.load_checkpoint(path, device=device)
    if trained_steps < 1:
        raise ValueError("untrained checkpoint cannot be used for inference")
    model.eval()
    raw_prompt = prompt.encode("utf-8")
    if len(raw_prompt) < 2:
        raise ValueError("prompt must contain at least 2 UTF-8 bytes")
    # The full prefix cannot exceed the model's exact training/config context.
    # Recompute logits on a sliding byte window; never claim long-context memory.
    context = list(raw_prompt[-model.config.max_sequence:])
    generated: list[int] = []
    log_probs: list[float] = []
    started = time.perf_counter()
    with torch.inference_mode():
        for _ in range(max_new_bytes):
            if cancel_event is not None and cancel_event.is_set():
                raise InterruptedError("candidate inference cancelled")
            inp = torch.tensor([context], dtype=torch.long, device=device)
            logits = model(inp).logits[0, -1]
            if not bool(torch.isfinite(logits).all().item()):
                raise ValueError("invalid non-finite model inference logits")
            prediction = int(torch.argmax(logits).item())
            probability = float(torch.softmax(logits, dim=-1)[prediction].item())
            if not math.isfinite(probability) or probability <= 0:
                raise ValueError("invalid model probability")
            generated.append(prediction)
            log_probs.append(math.log(probability))
            context = (context + [prediction])[-model.config.max_sequence:]
    if device == "cuda":
        torch.cuda.synchronize()
    elapsed = max(time.perf_counter() - started, 1e-9)
    candidate_bytes = bytes(generated)
    try:
        visible = candidate_bytes.decode("utf-8", errors="strict")
        valid_utf8 = True
    except UnicodeDecodeError:
        visible = candidate_bytes.decode("utf-8", errors="replace")
        valid_utf8 = False
    return {
        "status": "experimental_neural_byte_continuation",
        "model_kind": "trained_multiscale_gru_byte_predictor",
        "device": device,
        "trained_steps_in_checkpoint": trained_steps,
        "parameter_count": model.parameter_count,
        "context_bytes_used": min(len(raw_prompt), model.config.max_sequence),
        "generated_bytes": len(generated),
        "generated_hex": candidate_bytes.hex(),
        "generated_text_utf8_replacement": visible,
        "generated_valid_utf8": valid_utf8,
        "mean_chosen_token_log_probability": sum(log_probs) / len(log_probs),
        "bytes_per_second": len(generated) / elapsed,
        "response_kind": "ungrounded_neural_experiment",
        "source_citations": [],
        "verified_natural_language_answer": False,
        "promoted_to_chat": False,
        "internet_used": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Offline, ungrounded neural next-byte experiment; NOT Chat")
    parser.add_argument("--checkpoint", required=True, type=Path)
    prompt_source = parser.add_mutually_exclusive_group(required=True)
    prompt_source.add_argument("--prompt")
    prompt_source.add_argument("--prompt-stdin", action="store_true",
                               help="read bounded local prompt from stdin (no process-list exposure)")
    parser.add_argument("--confirm-local-checkpoint", action="store_true")
    parser.add_argument("--bytes", type=int, default=32)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    args = parser.parse_args(argv)
    try:
        if args.prompt_stdin:
            # The desktop pipes private prompts, never adding them to command
            # lines or persisting them to an unencrypted temporary file.
            raw = sys.stdin.buffer.read(2049)
            if len(raw) > 2048:
                raise ValueError("stdin prompt exceeds 2048 UTF-8 bytes")
            prompt = raw.decode("utf-8", errors="strict")
        else:
            prompt = args.prompt
        report = generate_candidate(
            args.checkpoint, prompt,
            trust_checkpoint=args.confirm_local_checkpoint,
            max_new_bytes=args.bytes, device=args.device)
    except (ValueError, PermissionError, RuntimeError, OSError, UnicodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
