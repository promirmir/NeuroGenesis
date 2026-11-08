"""Local, optional, actually conversational pretrained model; no external API.

The distributed Tk onefile EXE intentionally does not bundle these weights or
torch/transformers. An explicit download of the pinned Apache-2.0 model,
then a separately selected, trusted local Python runtime, is required.
No model may execute arbitrary repository Python code (trust_remote_code=False).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any

MODEL_ID = "Qwen/Qwen3-0.6B"
# Immutable upstream revision, established from the official model tree.
MODEL_REVISION = "c1899de289a04d12100db370d81485cdf75e47ca"
MODEL_CARD = "https://huggingface.co/Qwen/Qwen3-0.6B"
MODEL_LICENSE = "Apache-2.0"
ALLOWED_ASSETS = (
    "*.json", "*.safetensors", "tokenizer.model", "*.txt",
)
MAX_PROMPT_BYTES = 24_000
MAX_TURNS = 10
MAX_REPLY_TOKENS = 256


def validate_model_dir(directory: str | Path) -> Path:
    path = Path(directory).expanduser()
    if not path.is_dir() or path.is_symlink():
        raise ValueError("Wskaż istniejący lokalny katalog wytrenowanego modelu.")
    for name in ("config.json", "tokenizer_config.json"):
        candidate = path / name
        if not candidate.is_file() or candidate.is_symlink():
            raise ValueError("Brak wymaganego pliku modelu: " + name)
    safetensors = list(path.glob("*.safetensors"))
    if not safetensors or any(x.is_symlink() for x in safetensors):
        raise ValueError("Brak lokalnych zaufanych wag .safetensors.")
    if any(x.is_symlink() for x in path.iterdir()):
        raise ValueError("Katalog modelu ma nieakceptowane dowiązania.")
    if any(x.suffix in {".bin", ".pickle", ".pkl", ".py"} for x in path.iterdir()):
        raise ValueError("Katalog modelu zawiera niezaufane formaty wykonywalne/pickle.")
    return path


def validate_messages(raw: Any) -> list[dict[str, str]]:
    if type(raw) is not dict or set(raw) != {"messages"}:
        raise ValueError("Oczekiwano JSON: messages.")
    msgs = raw["messages"]
    if type(msgs) is not list or not 1 <= len(msgs) <= MAX_TURNS:
        raise ValueError("Wymagane 1–10 wiadomości.")
    out: list[dict[str, str]] = []
    for index, item in enumerate(msgs):
        if type(item) is not dict or set(item) != {"role", "content"}:
            raise ValueError("Nieprawidłowy format wiadomości.")
        role, content = item["role"], item["content"]
        if role not in ("user", "assistant") or type(content) is not str:
            raise ValueError("Tylko wiadomości użytkownika i asystenta.")
        if not content.strip() or len(content) > 1800:
            raise ValueError("Wiadomość przekracza limit 1800 znaków.")
        if role != ("user" if index % 2 == 0 else "assistant"):
            raise ValueError("Kolejność wiadomości musi się zmieniać.")
        out.append({"role": role, "content": content})
    if out[-1]["role"] != "user":
        raise ValueError("Ostatnia wiadomość musi pochodzić od użytkownika.")
    if len(json.dumps(out, ensure_ascii=False).encode("utf-8")) > MAX_PROMPT_BYTES:
        raise ValueError("Rozmowa zbyt długa.")
    return out


def download_local_model(destination: str | Path, *, confirm: bool = False) -> dict[str, Any]:
    """One-time explicit external download. Nothing launches or trains here."""
    if confirm is not True:
        raise PermissionError("Wymagane jawne potwierdzenie pobrania modelu i licencji.")
    dest = Path(destination).expanduser()
    if dest.exists() or dest.is_symlink():
        raise ValueError("Wybierz nowy, nieistniejący katalog docelowy.")
    if not dest.parent.is_dir():
        raise ValueError("Katalog nadrzędny nie istnieje.")
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("W wybranym Pythonie brakuje huggingface_hub.") from exc
    # Hugging Face downloads HTTPS (large, ~1.5 GB) upon the human's action.
    # Never use trust_remote_code, pickle, git scripts or arbitrary URLs.
    dest.mkdir(mode=0o700)
    try:
        downloaded = snapshot_download(
            repo_id=MODEL_ID,
            revision=MODEL_REVISION,
            local_dir=str(dest),
            allow_patterns=list(ALLOWED_ASSETS),
            ignore_patterns=["*.bin", "*.pt", "*.pth", "*.py", "*.pkl", "*.pickle"])
        validate_model_dir(downloaded)
        digest = hashlib.sha256()
        for file in sorted(dest.rglob("*")):
            if file.is_file() and not file.is_symlink():
                digest.update(str(file.relative_to(dest)).encode("utf-8"))
                digest.update(str(file.stat().st_size).encode("ascii"))
        return {
            "status": "local_pretrained_model_downloaded",
            "model_id": MODEL_ID,
            "revision": MODEL_REVISION,
            "license": MODEL_LICENSE,
            "source": MODEL_CARD,
            "directory": str(dest),
            "file_metadata_sha256": digest.hexdigest(),
            "trained_by_neurogenesis": False,
        }
    except Exception:
        # Failed / partial downloads are not silently considered usable.
        # Keep visible partial files for operator inspection, do NOT delete.
        raise


def load_local_runtime(model_dir: str | Path, *,
                       device: str = "cpu",
                       adapter_dir: str | Path | None = None):
    """Load trusted local safetensors exactly once for a conversation session."""
    base = validate_model_dir(model_dir)
    if device not in ("cpu", "cuda"):
        raise ValueError("Wybierz CPU albo CUDA.")
    if adapter_dir is not None:
        adapter = Path(adapter_dir)
        if not adapter.is_dir() or not (adapter / "adapter_config.json").is_file() or not list(adapter.glob("*.safetensors")):
            raise ValueError("Adapter LoRA musi być wcześniej lokalnie wytrenowany i zatwierdzony.")
    else:
        adapter = None
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
    except ImportError as exc:
        raise RuntimeError("Zainstaluj opcjonalne pakiety torch i transformers w wybranym Pythonie.") from exc
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA niedostępna.")
    tokenizer = AutoTokenizer.from_pretrained(
        base, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        base, local_files_only=True, use_safetensors=True,
        trust_remote_code=False, dtype=torch.float16 if device == "cuda" else torch.float32)
    model = model.to(device).eval()
    if adapter is not None:
        try:
            from peft import PeftModel
        except ImportError as exc:
            raise RuntimeError("Do lokalnego adaptera LoRA wymagany jest PEFT.") from exc
        model = PeftModel.from_pretrained(
            model, adapter, is_trainable=False, local_files_only=True).eval()
    return (torch, tokenizer, model, base, adapter is not None, device)


def respond_loaded(runtime, messages: list[dict[str, str]], *,
                   max_new_tokens: int = 128) -> dict[str, Any]:
    """Answer from weights already loaded into this local process."""
    validated = validate_messages({"messages": messages})
    if type(max_new_tokens) is not int or not 1 <= max_new_tokens <= MAX_REPLY_TOKENS:
        raise ValueError("Wybierz 1–256 tokenów odpowiedzi.")
    torch, tokenizer, model, base, has_adapter, device = runtime
    full = [{"role": "system", "content": (
        "Jesteś lokalnym asystentem NeuroGenesis. Nie udawaj źródeł ani wiedzy o zdarzeniach aktualnych. "
        "Gdy nie wiesz, przyznaj to. Nie masz autonomicznych działań poza tą rozmową."
    )}] + validated
    inputs = tokenizer.apply_chat_template(
        full, tokenize=True, add_generation_prompt=True,
        return_tensors="pt", enable_thinking=False).to(device)
    with torch.inference_mode():
        generated = model.generate(
            inputs, max_new_tokens=max_new_tokens,
            # Official Qwen3 non-thinking recommendations; greedy can repeat.
            do_sample=True, temperature=0.7, top_p=0.8, top_k=20,
            pad_token_id=tokenizer.eos_token_id)
    reply = tokenizer.decode(generated[0][inputs.shape[1]:],
                             skip_special_tokens=True).strip()
    return {
        "status": "local_conversational_model",
        "reply": reply,
        "model_dir": str(base),
        "adapter_used": has_adapter,
        "offline_inference": True,
        "trained_by_neurogenesis": False if not has_adapter else "local_adapter_only",
        "fact_checked": False,
        "source_citations": [],
    }


def respond_local(model_dir: str | Path, messages: list[dict[str, str]], *,
                  device: str = "cpu", max_new_tokens: int = 128,
                  adapter_dir: str | Path | None = None) -> dict[str, Any]:
    """One-shot backwards-compatible offline inference."""
    runtime = load_local_runtime(
        model_dir, device=device, adapter_dir=adapter_dir)
    return respond_loaded(runtime, messages, max_new_tokens=max_new_tokens)


def serve_local_stdio(model_dir: str | Path, *,
                      device: str = "cpu",
                      max_new_tokens: int = 128,
                      adapter_dir: str | Path | None = None) -> int:
    """Persistent local JSON-lines protocol; weights load ONCE per session.

    A separate explicit Python worker is used so the default frozen EXE
    stays dependency-light. Protocol messages do not contain URLs or code.
    """
    runtime = load_local_runtime(
        model_dir, device=device, adapter_dir=adapter_dir)
    print(json.dumps({"status": "local_model_ready", "offline": True}),
          flush=True)
    for line in iter(lambda: sys.stdin.buffer.readline(MAX_PROMPT_BYTES + 2), b""):
        try:
            if len(line) > MAX_PROMPT_BYTES + 1 or not line.endswith(b"\n"):
                raise ValueError("Wiadomość przekracza dopuszczalny limit.")
            payload = json.loads(line.decode("utf-8"))
            validated = validate_messages(payload)
            result = respond_loaded(runtime, validated,
                                    max_new_tokens=max_new_tokens)
        except (ValueError, PermissionError, RuntimeError, UnicodeError,
                json.JSONDecodeError) as exc:
            result = {"status": "local_model_error", "message": str(exc)}
        print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline dialogue or explicitly approved model download")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--download-model", action="store_true")
    mode.add_argument("--respond-stdin", action="store_true")
    mode.add_argument("--serve-stdio", action="store_true")
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--confirm-download-license", action="store_true")
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--adapter-dir", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.download_model:
            result = download_local_model(
                args.model_dir, confirm=args.confirm_download_license)
        elif args.serve_stdio:
            return serve_local_stdio(
                args.model_dir, device=args.device,
                max_new_tokens=args.max_new_tokens,
                adapter_dir=args.adapter_dir)
        else:
            raw = sys.stdin.buffer.read(MAX_PROMPT_BYTES + 1)
            if len(raw) > MAX_PROMPT_BYTES:
                raise ValueError("Wiadomości przekraczają limit.")
            payload = json.loads(raw.decode("utf-8"))
            messages = validate_messages(payload)
            result = respond_local(
                args.model_dir, messages, device=args.device,
                max_new_tokens=args.max_new_tokens,
                adapter_dir=args.adapter_dir)
    except (ValueError, PermissionError, OSError, RuntimeError, UnicodeError, ImportError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
