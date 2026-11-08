# Foundation Brain — paired checkpoint retention audit

**Public credit: Miron przy pomocy AI.** This is a strict research gate for byte-sequence prediction, not a proof of understanding or a neural chat launch.

## What the audit does

The optional `neurogenesis.foundation_gate` module takes two explicitly trusted **local trained** numerical checkpoints of the **same model configuration**: an incumbent and a candidate. It also takes two distinct, operator-authorized UTF-8 documents, held out from all training to the best of the operator's knowledge: one representing previously learned task/domain A, one a new task/domain B.

Both models run real PyTorch CPU (or explicitly available CUDA) on **the exact same old document** and then **the exact same new document**. The evaluator uses `foundation_train.evaluate_holdout` and its disjoint byte-window token-loss accounting. It records four real next-byte cross-entropy values in nats, total transitions, model steps, device and audit-source SHA-256 fingerprints. The audit never trains, rewrites checkpoints, modifies SQLite, accesses the Internet or promotes a model automatically.

**Numeric decision:** a candidate must (1) limit deterioration on old-domain CE to at most 5% (configurable `max_old_regression`) **and** (2) improve new-domain CE by at least 1% (configurable `min_new_improvement`). Failing either condition rejects the candidate for this narrow criterion. Passing both only satisfies this numeric gate; it does **not** establish accuracy in question answering, semantic reasoning, factual credibility, or readiness for chat.

The documents must be *genuinely held out*: reuse in training or iterative hyperparameter selection invalidates a prospective performance claim. A machine cannot infer that provenance from two raw text files; the current gate labels independence **operator asserted**. Do not tune a model repeatedly against the same audit files.

## Explicit local invocation

Prerequisite: optional PyTorch `pip install -e ".[foundation]"`, two trained local `.pt/.pth` checkpoint files and two UTF-8 documents to which the operator holds appropriate evaluation rights. Dataset files are **not uploaded to GitHub**.

```powershell
py -3.12 -m neurogenesis.foundation_gate --incumbent "C:\\private\\stable.pt" --candidate "C:\\private\\candidate.pt" --old-audit "C:\\private\\old-domain.txt" --new-audit "C:\\private\\new-domain.txt" --confirm-trusted-checkpoints --confirm-corpus-rights --sequence 32 --device cpu
```

Returns JSON with exact cross-entropy values, relative old-skill regression, relative new-task improvement, transparent thresholds, fingerprints, and `passes_numeric_retention_gate`. Regardless of outcome, `automatically_promoted=false` and `ready_for_semantic_chat=false`.

The existing Qt Training panel already offers source review, weight training and an isolated checkpoint-inference laboratory. This new audit starts as an independent CLI/worker test, not a misleading auto-upgrade GUI control. The current source-based chat and released Tk EXE are unchanged.

## Safety boundaries

- Explicit checkpoint trust and audit-corpus rights are required. Source files must be local non-symlink UTF-8 `.txt/.utf8`, between `2*sequence` and 64 KiB each, with different SHA-256 fingerprints. These constraints reduce accidental binary/oversize input; they cannot prove dataset independence or legal rights.
- Checkpoints must be separate, regular local `.pt/.pth` files, each with 1+ recorded training steps, loaded with `weights_only=True` through the established Foundation loader. Identical architectures and evaluation window lengths are required for a paired comparison.
- A configured sequence length 8–128 must not exceed model context. Device is explicitly CPU or CUDA; CUDA results are reported only if CUDA actually runs.
- The code does not access other machines, networks, public web pages, or private SQLite, nor does it publish raw documents, checkpoints, model outputs, or private operator paths in CI.
- Numerical CE tests and old/new retention are only one quality dimension. **No model may be promoted to end-user chat solely on these results.** Source grounding, calibrated abstention, independent held-out QA, performance versus Markov/Transformer controls, rights and rollback still require separate acceptance.

## CI evidence

`tests/test_foundation_gate.py` contains pure threshold tests (positive, forgetting and no-gain cases) and real PyTorch CPU proof on fictional local documents/checkpoints (four measurements, true checkpoint load, no source or checkpoint mutation, invalid rights/path/architecture refusal). The dedicated real Torch `.github/workflows/foundation-cpu.yml` runs it, alongside all existing Foundation and knowledge-trainer suites. The test emits **only artificial benchmark measurements** under `RETENTION_AUDIT_CPU_METRICS`; it cannot justify a worldwide AI quality claim.

## Next scientific tasks

Develop genuinely independent licensed natural-language, contextual question-answering and factual source checks; run prospective baseline-matched comparisons and per-domain forgetting on previously unused data. Introduce candidate-vs-incumbent checkpoint **promotion only after** complete multi-task gates, explicit user approval and rollback tests. See issue #18 and docs/VISION.md.

## Verified numeric gate milestone — PR #33 merged (November 8, 2026)

PR #33 merged to main `fd4ab6a723baad237d583d62991dbfdcd84b3f74` after Python 3.11–3.13, real CPU PyTorch, privacy and frozen Tk EXE checks. In fictional CPU data, old-domain CE improved 5.7167409→5.6910159, but new-task CE only 5.7461666→5.7415593 (~0.08%); the configurable 1% gate correctly **rejected** this candidate. A report passing a gate later must still not auto-promote. Follow-up PR #34 enabled real resumed weights on separately approved datasets; evaluate any such update against truly unused audit files.
