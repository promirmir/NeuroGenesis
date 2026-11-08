# NeuroGenesis — prospective source-QA acceptance gate

**Public credit: Miron przy pomocy AI.** This is a *numerical, literal-citation and abstention* acceptance criterion, NOT truth verification, neural reasoning or an AGI benchmark.

## Why this was added

The existing `qa_eval` measures whether a question receives an expected literal excerpt from an expected URL and whether unsupported questions are refused. Six previously seen fictional development questions included a **false citation**, and improving a rule on those same six questions cannot establish independent generalization. A score of 100% on a tiny corpus would be equally misleading.

`neurogenesis.qa_acceptance` adds an explicit separate **prospective** audit JSONL, a distinct development audit JSONL, question-overlap checks, conservative statistical intervals, and an abstain-all baseline. It uses the same real read-only SQLite answer path, never modifies the brain or private history, and never transmits questions to GitHub.

## Evaluation contract

- Input: existing private SQLite with source excerpts, a local *development* JSONL and a different local *prospective* JSONL, both in the same schema used by [QA_EVALUATION.md](QA_EVALUATION.md). A positive case names an exact URL and verbatim text expected inside the quote; an unsupported case requires refusal.
- Both JSONLs must contain positive and negative cases, and the prospective audit needs at least **30 supported and 60 unsupported** examples by default. Numbers are **minimums for scoring**, not proof of sample sufficiency. Source rights and absence of use in training/tuning must be explicitly asserted.
- Exact normalized questions may not appear in both sets, and duplicated prospective questions are rejected. This detects direct overlap but **does not detect paraphrases, near-duplicate passages, cross-document contamination or repeated tuning**. Human governance and cryptographic dataset versioning are needed.
- The report includes observed literal quote recall, false-citation rate, **two-sided approximately 95% Wilson confidence interval** for both rates, and comparison with an always-abstain baseline. For positive evidence and unsupported examples, error asymmetry matters.
- Default numeric acceptance requires **at least 70% Wilson lower bound on supported literal recall**, **no more than 5% Wilson upper bound on unsupported false-citation rate**, and at least **10 percentage points** higher strict score than abstain-all. All must hold. With only 60 negative cases and zero observed errors, Wilson upper bound is *above* 5%, so a misleading 100% on a small set cannot pass.
- The report always states `independently_fact_checked=false`, `source_quote_truth_verified=false`, `ready_for_semantic_chat=false`, `automatically_promoted=false`. Its boolean `passes_numeric_prospective_gate` is NOT a deployment authorization.

## Offline invocation

Prepare two local, rights-cleared, **genuinely separate** JSONL files. **Do not** upload user files, text, or downloaded material to public GitHub.

```powershell
py -3.12 -m neurogenesis.qa_acceptance --db "C:\\private\\experiences.sqlite3" --development-audit "C:\\private\\dev-qa.jsonl" --prospective-audit "C:\\private\\unseen-qa.jsonl" --confirm-corpus-rights --confirm-untouched
```

Returns JSON of aggregate counts, SHA-256 fingerprints, confidence intervals, refusal rates, baseline score and measured local SQLite retrieval latency. **No raw questions, excerpts, URLs or paths are in output**.

## CI and honest evidence

`tests/test_qa_acceptance.py` runs against a fully fictional, generated SQLite corpus, with 40 supported and 100 unsupported synthetic cases and an independent development file. It checks zero observed negative errors can still have nonzero uncertainty, numeric PASS on the easy fictional set, FAIL on a case with unsupported claim additions sharing topic terms, refusal of overlapping audits, refusal of insufficient samples, baseline comparison and strict no-DB-mutation privacy.

This is a **code regression and gate-behavior test**, not a prospective empirical result. The synthetic questions and sources live in public test code and have therefore been seen during development. Real independent QA is still unperformed. The dedicated `qa-acceptance.yml` and standard Python 3.11–3.13 / Windows EXE / Qt regression checks are required before merge.

## Remaining scientific barriers

1. Secure and freeze rights-cleared **human-authored** prospective source and QA audit material, independently collected across domains and publishers. Avoid retuning to the audit and include paraphrases, negation, time-sensitive changes, unsupported premises and source conflict cases.
2. Measure **actual answer truth and contextual reasoning**, not merely literal citation. Distinguish supported quote vs logically entailed conclusion. Compare against abstain-all, BM25/RAG and appropriately matched trained model baselines.
3. Test neural Foundation Brain retrieval-conditioned answers and old-skill preservation prospectively; current byte continuation remains an experimental separate lab.
4. Operator-controlled rollback, physical GPU measurements, legally compliant Qt packaging, and full independent security audit remain required for v1.

No AI consciousness, human brain equivalence, AGI, or competitive frontier reasoning is implied by an acceptance-gate implementation.
