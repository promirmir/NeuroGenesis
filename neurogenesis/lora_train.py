"""Bounded offline PEFT/LoRA supervised dialogue tuning from licensed UTF-8 TXT.

Unlike the tiny experimental next-byte GRU, this updates *only* trainable
LoRA adapter weights for an existing locally downloaded pretrained LLM.
No downloads, no remote code, no automatic deployment, no claim of general
intelligence, and no private corpus in process argv beyond a file path.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import tempfile
import time
from typing import Any

from .local_dialogue import validate_model_dir

MAX_TEXT_BYTES = 32 * 1024 * 1024


def parse_dialogues(text: str) -> list[tuple[str, str]]:
    """Strict line-oriented role schema: USER/ASSISTANT or Polish equivalent.

    Multi-turn files generate consecutive adjacent supervised pairs. There is
    no unsourced synthetic answer generation, and malformed role order fails.
    """
    if type(text) is not str or len(text.encode("utf-8")) > MAX_TEXT_BYTES:
        raise ValueError("Tekst treningowy przekracza limit 32 MiB.")
    pairs: list[tuple[str, str]] = []
    pending = None
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        up = s.upper()
        if up.startswith(("USER:", "UŻYTKOWNIK:")):
            if pending is not None:
                raise ValueError("Brak odpowiedzi ASSISTANT po poprzednim pytaniu.")
            pending = s.split(":", 1)[1].strip()
            if not 3 <= len(pending) <= 1800:
                raise ValueError("Pytanie powinno mieć 3–1800 znaków.")
        elif up.startswith(("ASSISTANT:", "ASYSTENT:")):
            if pending is None:
                raise ValueError("Odpowiedź bez pytania.")
            answer = s.split(":", 1)[1].strip()
            if not 2 <= len(answer) <= 6000:
                raise ValueError("Odpowiedź powinna mieć 2–6000 znaków.")
            pairs.append((pending, answer))
            pending = None
        else:
            raise ValueError("Każda linia ma zaczynać się USER:/ASSISTANT: lub UŻYTKOWNIK:/ASYSTENT:.")
    if pending is not None:
        raise ValueError("Plik kończy się pytaniem bez odpowiedzi.")
    if len(pairs) < 20:
        raise ValueError("LoRA wymaga minimum 20 par dialogowych.")
    if len(set(pairs)) != len(pairs):
        raise ValueError("Duplikaty par muszą być usunięte przed ewaluacją.")
    if len({p[0] for p in pairs}) != len(pairs):
        raise ValueError("Powtarzające się pytania zaburzają holdout; usuń duplikaty.")
    return pairs


def masked_assistant_tokens(tokenizer: Any, question: str,
                            answer: str, *, seq: int) -> tuple[list[int], list[int]] | None:
    """Match the *generation* prefix and compute loss on assistant tokens only.

    Qwen3's add_generation_prompt can contain an empty <think></think>
    prefix that historical completed-turn serialization does not include.
    Avoid inferring alignment from full-chat rendering.
    """
    prefix = tokenizer.apply_chat_template(
        [{"role": "user", "content": question}],
        tokenize=True, add_generation_prompt=True, enable_thinking=False)
    if not isinstance(prefix, list):
        raise ValueError("Tokenizer nie obsługuje szablonu rozmowy.")
    answer_ids = tokenizer(answer, add_special_tokens=False).input_ids
    if not isinstance(answer_ids, list) or tokenizer.eos_token_id is None:
        raise ValueError("Brak tokenów odpowiedzi albo EOS.")
    if len(prefix) >= seq - 4:
        return None
    tokens = (prefix + answer_ids + [tokenizer.eos_token_id])[:seq]
    labels = [-100] * len(prefix) + tokens[len(prefix):]
    if len(labels) != len(tokens) or sum(x != -100 for x in labels) < 2:
        return None
    return tokens, labels


def validate_training_paths(model_dir: str | Path, input_txt: str | Path,
                            output_dir: str | Path, *, rights: bool,
                            trust_model: bool, steps: int,
                            seq: int, device: str) -> tuple[Path, Path, Path]:
    if rights is not True or trust_model is not True:
        raise PermissionError("Potwierdź prawa do korpusu i zaufanie do lokalnych wag.")
    model = validate_model_dir(model_dir)
    source = Path(input_txt)
    if not source.is_file() or source.is_symlink() or source.suffix.lower() != ".txt":
        raise ValueError("Wybierz regularny lokalny plik TXT, nie dowiązanie.")
    if not 1024 <= source.stat().st_size <= MAX_TEXT_BYTES:
        raise ValueError("TXT musi mieć 1 KiB–32 MiB.")
    destination = Path(output_dir)
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir():
        raise ValueError("Wskaż nowy, nieistniejący katalog dla adaptera.")
    if destination.resolve() in (model.resolve(), source.resolve()):
        raise ValueError("Nie nadpisuj wag bazowych ani danych treningowych.")
    if type(steps) is not int or not 1 <= steps <= 1000 or type(seq) is not int or not 96 <= seq <= 512:
        raise ValueError("Kroki 1–1000, kontekst 96–512 tokenów.")
    if device not in ("cpu", "cuda"):
        raise ValueError("Dozwolone CPU lub CUDA.")
    return model, source, destination


def finetune_local_dialogue(model_dir: str | Path, input_txt: str | Path,
                            output_dir: str | Path, *, rights: bool = False,
                            trust_model: bool = False, steps: int = 30,
                            seq: int = 256, device: str = "cpu",
                            seed: int = 1234) -> dict[str, Any]:
    """Train candidate LoRA; never activate in chat without operator selection."""
    model_path, source, destination = validate_training_paths(
        model_dir, input_txt, output_dir, rights=rights, trust_model=trust_model,
        steps=steps, seq=seq, device=device)
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("Nieprawidłowe ziarno losowania.")
    data = source.read_bytes()
    try:
        pairs = parse_dialogues(data.decode("utf-8", errors="strict"))
    except UnicodeError as exc:
        raise ValueError("TXT musi być w UTF-8.") from exc
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import LoraConfig, get_peft_model
    except ImportError as exc:
        raise RuntimeError("Wymagane torch, transformers, peft; zainstaluj pakiet [dialogue].") from exc
    if device == "cuda" and not torch.cuda.is_available():
        raise ValueError("CUDA niedostępna.")
    randomizer = random.Random(seed)
    pairs = list(pairs)
    randomizer.shuffle(pairs)
    count_holdout = max(2, len(pairs) // 10)
    training, holdout = pairs[count_holdout:], pairs[:count_holdout]
    torch.manual_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, local_files_only=True, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, local_files_only=True, use_safetensors=True,
        trust_remote_code=False,
        dtype=torch.float16 if device == "cuda" else torch.float32)
    model.to(device)
    adapter = get_peft_model(
        model, LoraConfig(
            r=8, lora_alpha=16, lora_dropout=0.05, bias="none",
            target_modules=["q_proj", "v_proj"], task_type="CAUSAL_LM"))
    trainable = sum(p.numel() for p in adapter.parameters() if p.requires_grad)
    if trainable < 1:
        raise ValueError("Żaden parametr LoRA nie jest trenowany.")

    def encode_pair(pair):
        encoded = masked_assistant_tokens(tokenizer, pair[0], pair[1], seq=seq)
        if encoded is None:
            return None
        tokens, labels = encoded
        return (
            torch.tensor([tokens], dtype=torch.long, device=device),
            torch.tensor([labels], dtype=torch.long, device=device),
        )
    train = [x for pair in training if (x := encode_pair(pair)) is not None]
    held = [x for pair in holdout if (x := encode_pair(pair)) is not None]
    if len(train) < 10 or len(held) < 2:
        raise ValueError("Za mało odpowiedzi mieści się w oknie tokenów; skróć tekst.")
    optimizer = torch.optim.AdamW(
        (p for p in adapter.parameters() if p.requires_grad),
        lr=0.00015, weight_decay=0.01)

    def holdout_loss():
        adapter.eval()
        total = 0.0
        with torch.inference_mode():
            for x, y in held:
                loss = float(adapter(input_ids=x, labels=y).loss.item())
                if not math.isfinite(loss):
                    raise ValueError("Niefinitywna strata walidacyjna.")
                total += loss
        return total / len(held)

    before = holdout_loss()
    start = time.monotonic()
    adapter.train()
    losses = []
    for i in range(steps):
        x, y = train[i % len(train)]
        optimizer.zero_grad(set_to_none=True)
        loss = adapter(input_ids=x, labels=y).loss
        if not bool(torch.isfinite(loss).item()):
            raise ValueError("Niefinitywna strata; adapter nie zostanie zapisany.")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(
            (p for p in adapter.parameters() if p.requires_grad), 1.0)
        optimizer.step()
        losses.append(float(loss.detach().item()))
    after = holdout_loss()
    elapsed = max(1e-9, time.monotonic() - start)
    # Save a candidate in a new directory; never replace existing adapters.
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=".ng-lora-") as tmp:
        staged = Path(tmp) / "adapter"
        adapter.save_pretrained(staged, safe_serialization=True)
        if not (staged / "adapter_config.json").is_file() or not list(staged.glob("*.safetensors")):
            raise ValueError("Adapter nie zapisał wymaganych plików.")
        report = {
            "status": "local_lora_candidate_trained",
            "trainable_parameters": trainable,
            "model_type": "pretrained_transformer_with_lora",
            "training_pairs": len(train),
            "holdout_pairs": len(held),
            "train_steps": steps,
            "device": device,
            "holdout_ce_before": before,
            "holdout_ce_after": after,
            "heldout_improved": after < before,
            "final_train_loss": losses[-1],
            "train_steps_per_second": steps / elapsed,
            "training_file_sha256": hashlib.sha256(data).hexdigest(),
            "candidate_only": True,
            "deployed_to_chat": False,
            "generalization_verified": False,
            "autonomous_self_improvement": False,
        }
        (staged / "training_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        if destination.exists():
            raise FileExistsError("Katalog docelowy został zajęty w czasie treningu.")
        staged.rename(destination)
    report["adapter_dir"] = str(destination)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline LoRA candidate tuning from dialogue TXT")
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confirm-corpus-rights", action="store_true")
    parser.add_argument("--confirm-trusted-model", action="store_true")
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--sequence", type=int, default=256)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--seed", type=int, default=1234)
    args = parser.parse_args(argv)
    try:
        report = finetune_local_dialogue(
            args.model_dir, args.input, args.output,
            rights=args.confirm_corpus_rights,
            trust_model=args.confirm_trusted_model,
            steps=args.steps, seq=args.sequence, device=args.device,
            seed=args.seed)
    except (ValueError, PermissionError, RuntimeError, OSError, UnicodeError, ImportError) as exc:
        parser.error(str(exc))
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
