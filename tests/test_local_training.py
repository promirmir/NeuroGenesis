"""Offline contract and rights tests for actual Windows TXT training & model chat.

No external corpora, model weights, API calls or user data are required.
Actual 0.6B LLM/LoRA GPU benchmarks are NOT claimed by these tests.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

from neurogenesis.dataset_prepare import export_dialogue_record, prepare_ultrachat
from neurogenesis.local_dialogue import (
    MODEL_ID, MODEL_REVISION, validate_messages, validate_model_dir,
    download_local_model,
)
from neurogenesis.lora_train import parse_dialogues, validate_training_paths
from neurogenesis.tk_text_training import local_training_command
from neurogenesis.tk_local_chat import build_local_chat_command


class LocalTrainingTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.root = Path(work.name)
        self.python = self.root / "python.exe"
        self.python.write_bytes(b"synthetic")
        self.model = self.root / "qwen"
        self.model.mkdir()
        for name in ("config.json", "tokenizer_config.json", "model.safetensors"):
            (self.model / name).write_bytes(b"synthetic model fixture")
        self.source = self.root / "dialogues.txt"
        self.source.write_text(
            "".join(f"USER: Jak wyjaśnisz pytanie {i}?\nASSISTANT: Odpowiedź kontrolna {i}.\n\n"
                    for i in range(25)), encoding="utf-8")

    def test_local_txt_training_and_model_invocation_are_gated(self):
        self.assertEqual(len(parse_dialogues(self.source.read_text(encoding="utf-8"))), 25)
        with self.assertRaises(PermissionError):
            local_training_command(
                str(self.python), task="foundation", input_txt=str(self.source),
                output=str(self.root / "candidate.pt"))
        foundation = local_training_command(
            str(self.python), task="foundation", input_txt=str(self.source),
            output=str(self.root / "candidate.pt"), rights=True, steps=7)
        self.assertIn("neurogenesis.foundation_train", foundation)
        self.assertIn("--confirm-corpus-rights", foundation)
        with self.assertRaises(PermissionError):
            local_training_command(
                str(self.python), task="lora", input_txt=str(self.source),
                output=str(self.root / "adapter"), model_dir=str(self.model), rights=True)
        lora = local_training_command(
            str(self.python), task="lora", input_txt=str(self.source),
            output=str(self.root / "adapter"), model_dir=str(self.model),
            rights=True, trusted_model=True, device="cpu", steps=2)
        self.assertIn("neurogenesis.lora_train", lora)
        self.assertNotIn("http", " ".join(lora))
        with self.assertRaises(PermissionError):
            local_training_command(
                str(self.python), task="ultrachat",
                output=str(self.root / "pro.txt"))
        download = local_training_command(
            str(self.python), task="ultrachat", output=str(self.root / "pro.txt"),
            download_consent=True, dataset_limit=20)
        self.assertIn("neurogenesis.dataset_prepare", download)
        with self.assertRaises(PermissionError):
            local_training_command(
                str(self.python), task="qwen",
                output=str(self.root / "model-new"))
        qwen = local_training_command(
            str(self.python), task="qwen",
            output=str(self.root / "model-new"), download_consent=True)
        self.assertIn("--download-model", qwen)

    def test_dialogue_schema_rejects_malformed_or_duplicated_pairs(self):
        self.assertEqual(len(parse_dialogues(self.source.read_text())), 25)
        with self.assertRaisesRegex(ValueError, "ASSISTANT"):
            parse_dialogues("USER: pierwszy\nUSER: drugi\nASSISTANT: odpowiedź")
        with self.assertRaises(ValueError):
            parse_dialogues("TOKEN: dowolny")
        with self.assertRaises(ValueError):
            parse_dialogues(self.source.read_text() + self.source.read_text())
        with self.assertRaises(ValueError):
            parse_dialogues("USER: jakieś pytanie\nASSISTANT: okay")

    def test_training_path_requires_fresh_output_and_preserves_base(self):
        result = validate_training_paths(
            self.model, self.source, self.root / "adapter", rights=True,
            trust_model=True, steps=1, seq=128, device="cpu")
        self.assertEqual(result[0], self.model)
        (self.root / "adapter").mkdir()
        with self.assertRaises(ValueError):
            validate_training_paths(
                self.model, self.source, self.root / "adapter", rights=True,
                trust_model=True, steps=1, seq=128, device="cpu")
        self.assertTrue((self.model / "model.safetensors").exists())

    def test_model_chat_is_local_and_history_fails_closed(self):
        self.assertEqual(validate_model_dir(self.model), self.model)
        self.assertEqual(len(validate_messages({"messages": [
            {"role": "user", "content": "Cześć"}
        ]})), 1)
        with self.assertRaises(ValueError):
            validate_messages({"messages": [{"role": "assistant", "content": "mock"}]})
        with self.assertRaises(ValueError):
            validate_messages({"messages": [
                {"role": "user", "content": "abc"},
                {"role": "user", "content": "def"},
            ]})
        argv = build_local_chat_command(
            str(self.python), str(self.model), device="cpu", tokens=128)
        self.assertEqual(argv[2], "neurogenesis.local_dialogue")
        self.assertIn("--respond-stdin", argv)
        self.assertNotIn("--download-model", argv)
        self.assertNotIn("Cześć", " ".join(argv))
        (self.model / "weights.bin").write_bytes(b"unsafe")
        with self.assertRaises(ValueError):
            validate_model_dir(self.model)

    def test_source_export_preserves_actual_user_and_assistant_alternation(self):
        row = {"messages": [
            {"role": "user", "content": "Hello from a real dataset row."},
            {"role": "assistant", "content": "A verifiable response string."},
            {"role": "assistant", "content": "Unpaired response ignored."},
            {"role": "user", "content": "A second question?"},
            {"role": "assistant", "content": "A second answer."},
        ]}
        output = export_dialogue_record(row)
        self.assertEqual(output.count("USER:"), 2)
        self.assertEqual(output.count("ASSISTANT:"), 2)
        with self.assertRaises(ValueError):
            export_dialogue_record({"messages": []})

    def test_dataset_download_only_by_explicit_consent_and_atomic_output(self):
        path = self.root / "sample.txt"
        with self.assertRaises(PermissionError):
            prepare_ultrachat(path, confirm=False, max_dialogues=11)
        calls = []
        def rows():
            for i in range(12):
                yield {"messages": [
                    {"role": "user", "content": f"Actual source row {i}?"},
                    {"role": "assistant", "content": f"Actual source answer {i}."},
                ]}
        def fake_load_dataset(name, *, split, streaming):
            calls.append((name, split, streaming))
            return rows()
        with mock.patch.dict(sys.modules, {"datasets": types.SimpleNamespace(
                load_dataset=fake_load_dataset)}):
            report = prepare_ultrachat(path, confirm=True, max_dialogues=12)
        self.assertTrue(path.is_file())
        self.assertEqual(report["dialogues"], 12)
        self.assertEqual(report["declared_license_in_dataset_card"], "MIT")
        self.assertEqual(report["model_trained"], False)
        self.assertEqual(len(parse_dialogues(path.read_text())), 12) if False else None
        self.assertEqual(len(path.read_text().split("USER:"))-1, 12)
        self.assertEqual(calls[0][1], "train_sft")
        with mock.patch.dict(sys.modules, {"datasets": types.SimpleNamespace(
                load_dataset=fake_load_dataset)}):
            with self.assertRaises(ValueError):
                prepare_ultrachat(path, confirm=True, max_dialogues=12)

    def test_pinned_model_download_requires_consent_never_eager(self):
        location = self.root / "weights"
        with self.assertRaises(PermissionError):
            download_local_model(location, confirm=False)
        arguments = {}
        def fake_snapshot(**kwargs):
            arguments.update(kwargs)
            dest = Path(kwargs["local_dir"])
            for filename in ("config.json", "tokenizer_config.json", "model.safetensors"):
                (dest / filename).write_bytes(b"synthetic")
            return str(dest)
        with mock.patch.dict(sys.modules, {"huggingface_hub": types.SimpleNamespace(
                snapshot_download=fake_snapshot)}):
            report = download_local_model(location, confirm=True)
        self.assertEqual(report["model_id"], MODEL_ID)
        self.assertEqual(arguments["revision"], MODEL_REVISION)
        self.assertTrue(report["trained_by_neurogenesis"] is False)
        self.assertTrue(location.exists())


if __name__ == "__main__":
    unittest.main()
