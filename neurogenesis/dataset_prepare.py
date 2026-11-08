"""Auditable, opt-in preparation of high-quality *external* dialogue data.

This does not train a model or approve data automatically. Only one
operator-chosen, documented Hugging Face dataset ID is supported. Downloads
are HTTPS initiated explicitly, never silently on application launch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
from typing import Any

DATASET = "HuggingFaceH4/ultrachat_200k"
SPLIT = "train_sft"
CARD = "https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k"
LABEL = "UltraChat 200k / angielskie dialogi / dataset card MIT"
MAX_BYTES = 32 * 1024 * 1024


def export_dialogue_record(record: Any) -> str:
    """Convert HF messages to explicitly delimited UTF-8 training text.

    The generated pairs retain turn order; no made-up assistant replies.
    """
    if type(record) is not dict or type(record.get("messages")) is not list:
        raise ValueError("Dataset example lacks conversational messages.")
    out = []
    messages = record["messages"]
    for entry in messages:
        if type(entry) is not dict:
            continue
        role, content = entry.get("role"), entry.get("content")
        if role not in ("user", "assistant") or type(content) is not str:
            continue
        content = " ".join(content.split())
        if not 3 <= len(content) <= 6000:
            continue
        marker = "USER:" if role == "user" else "ASSISTANT:"
        out.append(marker + " " + content)
    if len(out) < 2 or not out[0].startswith("USER:"):
        raise ValueError("No valid user/assistant exchange in dataset record.")
    if not any(s.startswith("ASSISTANT:") for s in out):
        raise ValueError("No valid assistant response in dataset record.")
    return "\n".join(out) + "\n\n"


def prepare_ultrachat(output: str | Path, *, confirm: bool = False,
                      max_dialogues: int = 300) -> dict[str, Any]:
    """Download a bounded, human-authorized subset and write new local TXT.

    The data license is not independently certified. The operator must read
    the upstream dataset card and decide whether use is appropriate.
    """
    if confirm is not True:
        raise PermissionError("Potwierdź zapoznanie się z kartą danych i warunkami wykorzystania.")
    if type(max_dialogues) is not int or not 10 <= max_dialogues <= 1500:
        raise ValueError("Ustaw 10–1500 dialogów.")
    output = Path(output).expanduser()
    if output.suffix.lower() != ".txt" or output.exists() or output.is_symlink():
        raise ValueError("Wybierz nową, nieistniejącą ścieżkę .txt.")
    if not output.parent.is_dir():
        raise ValueError("Katalog docelowy nie istnieje.")
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise RuntimeError("Zainstaluj pakiet datasets w wybranym Pythonie.") from exc

    corpus = load_dataset(DATASET, split=SPLIT, streaming=True)
    count, total = 0, 0
    unique = set()
    temp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix=".ng-corpus-",
                                         suffix=".tmp", dir=output.parent,
                                         delete=False) as fh:
            temp = Path(fh.name)
            for record in corpus:
                try:
                    fragment = export_dialogue_record(record)
                except ValueError:
                    continue
                digest = hashlib.sha256(fragment.encode("utf-8")).digest()
                if digest in unique:
                    continue
                encoded = fragment.encode("utf-8")
                if total + len(encoded) > MAX_BYTES:
                    break
                fh.write(encoded)
                unique.add(digest)
                total += len(encoded)
                count += 1
                if count >= max_dialogues:
                    break
        if count < 10 or total < 1024:
            raise ValueError("Źródło zwróciło za mało poprawnych dialogów.")
        if output.exists():
            raise FileExistsError("Plik wynikowy już istnieje.")
        temp.rename(output)
        temp = None
        file_sha = hashlib.sha256(output.read_bytes()).hexdigest()
        return {
            "status": "opt_in_dataset_export",
            "source": DATASET,
            "split": SPLIT,
            "dataset_card": CARD,
            "declared_license_in_dataset_card": "MIT",
            "language": "English",
            "dialogues": count,
            "bytes": total,
            "sha256": file_sha,
            "file": str(output),
            "source_review_required_for_training": True,
            "model_trained": False,
            "model_deployed": False,
        }
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Opt-in professional dialogue corpus export, not training")
    parser.add_argument("--source", choices=("ultrachat",), default="ultrachat")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=300)
    parser.add_argument("--confirm-source-license", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = prepare_ultrachat(
            args.output, confirm=args.confirm_source_license,
            max_dialogues=args.limit)
    except (ValueError, PermissionError, RuntimeError, OSError, ImportError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
