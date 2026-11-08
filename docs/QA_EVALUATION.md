# NeuroGenesis — reproducible, local grounded-QA acceptance evaluator

**Public credit: Miron przy pomocy AI.** This evaluator measures citation fidelity, not factual truth or model reasoning.

## Purpose

The existing source-based dialogue can return a verbatim 450-character excerpt when lexical overlap is sufficient. This may be a **correct citation of an unreliable statement**, an irrelevant quote, or an unjustified answer to a question unsupported by the source. Comparing only training loss or the number of ingested pages does not reveal those failures.

`neurogenesis.qa_eval` introduces a bounded **read-only** evaluation of question-to-quoted-evidence matching from the existing local versioned SQLite knowledge store. It never trains weights or invokes the legacy brain, network, a hosted LLM, an external API or user filesystem outside the two explicitly supplied input files.

## Audit format (private UTF-8 JSONL)

Each line contains one JSON object. Positive cases must specify the exact source URL and a literal excerpt span from an **independent operator-reviewed** reference. Negative cases must omit any expected answer/citation.

```jsonl
{"question":"Co opisuje raport Delta?","answerable":true,"expected_source_url":"https://example.org/delta","required_quote":"opisuje badanie trwałości"}
{"question":"Dlaczego raport Delta dowodzi świadomości?","answerable":false}
```

This example is **synthetic**, not a claim about a real site. Keep this file PRIVATE and never commit real questions or personal corpus files. 1–256 records, each ≤4 KiB, nonempty distinct question strings, both positive and negative cases mandatory; question length ≤512 characters. Quotes use case-insensitive literal matching and are never interpreted semantically.

## Run the evaluator

```powershell
py -3.12 -m neurogenesis.qa_eval --db "C:\\private\\experiences.sqlite3" --audit "C:\\private\\heldout-qa.jsonl" --confirm-corpus-rights --confirm-held-out
```

Only a trusted **existing** local SQLite file is opened in read-only mode; no migration or blank DB is created. The evaluator returns a JSON object containing only aggregate measurements and the local audit-file SHA-256 fingerprint, **never the raw questions, source text, user filenames or full URLs**. Two explicit confirmations are required: audit corpus rights and assertion that questions/expected source quotes were *not* used for training, prompt selection, tuning or implementation decisions.

A developer can run the same evaluation on another unchanged database or a candidate retrieval algorithm while preserving the audit set. Keep the dataset fixed for honest comparison; repeated tuning against it invalidates a prospective "held out" claim.

## Exact interpretation

- `supported_exact_quote_recall`: fraction of positive items for which the app actually returned a quoted excerpt containing the operator-specified literal span from the exact operator-specified source URL.
- `supported_source_hit_rate`: fraction of positive items citing the right source URL, regardless of whether they quoted the required span.
- `quote_precision_all_answered`: correct exact URL + required text matches divided by *all* returned answers, including answers to unsupported questions.
- `unsupported_abstention_rate`: fraction of negative items for which the system returned no evidence, and `unsupported_false_citation_rate` is its complement.
- `overall_strict_fixture_accuracy`: positives with required literal citation plus negatives that abstained, divided by all cases.
- `latency_p50_ms` and `latency_p95_ms`: actual query-only SQLite + lexical retrieval latency on the current hardware, **not GUI response/Internet time**.

The main task is explicitly named `literal_evidence_qa_and_abstention_not_semantic_or_truth_accuracy`. This is *not a natural-language answer correctness benchmark* and does not prove facts, publisher independence, contradiction resolution, neural competence or AGI. The audit cannot prove source/license ownership or that the test set is genuinely unseen; it accepts those as operator declarations.

## Verified gates and next use

`tests/test_qa_eval.py` uses a small **fictional** local source-and-Q/A fixture to check citation attribution, positive recall, negative abstention, and an intentionally overlapping unsupported question. The benchmark *must expose* its false-positive risk rather than fabricate 100% reliability. It additionally checks no SQLite writes, private memory retention, explicit consent, invalid JSON/UTF-8, no accidental DB creation, and aggregate-only CLI output.

The Python 3.11–3.13 and Windows frozen EXE workflows run these tests without external packages; actual PyTorch and Qt workflows remain independent. No benchmark run against independent licensed human-written QA or real public sites is claimed until supplied and evaluated with verifiable rights.

## Next required model-quality stage

Use a genuinely independent rights-cleared corpus and domain-specific Q/A sets. Report quality against a simple lexical baseline and meaningful neural model alternative under comparable budgets, check old-task regression and factual correctness, and only then consider source-grounded neural chat promotion. The current tiny synthetic fixture is an engineering smoke test, not generalization evidence.
