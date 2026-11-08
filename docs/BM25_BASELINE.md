# Offline BM25 versus current source evidence (benchmark-only)

**Credit: Miron przy pomocy AI.** This is a non-neural *retrieval baseline*, not a new product chat engine.

## Research purpose

To demonstrate the real value of new neural or heuristic retrieval strategies, NeuroGenesis needs a strong, established classical comparator. `neurogenesis.qa_baselines` implements a bounded **BM25 (k1=1.2, b=0.75)** passage ranker over the **same latest-revision private SQLite evidence** used by the current source-cited conversation. It ranks actual term frequencies using document length and inverse document frequency; no model download, remote API or network calls.

For each question in an explicitly rights-cleared, supposedly untouched local QA JSONL, the benchmark evaluates **two algorithms against identical stored passages and question labels**:

1. Existing production `knowledge.answer_question` returns up to two verbatim citations, requiring a minimum term overlap and conservative Polish yes/no guard.
2. Independent BM25 control retrieves the highest-scoring latest-revision excerpt, subject to the **same minimum lexical term-overlap and yes/no negation gates**, never claimed to entail the user question. Its term-frequency weighting differs, and it is NOT deployed.

For both, the benchmark reports exact expected literal quote+URL recall, unsupported false-citation rate, strict fixture score and measured median lookup duration. It also reports the difference in strict fixture score, but does not select or deploy a winning algorithm. A high BM25 ranking can be a confidently wrong response to an unsupported proposition; the benchmark must show these errors instead of hiding them.

The baseline reads at most **4,096 latest-revision passages**, with a per-passage cap of 600 tokens, and raises rather than scanning larger private databases. A real BM25 system for larger databases would use an efficient inverted index rather than this bounded in-memory audit reference.

## Offline invocation

Prepare a local JSONL with supported examples (`question`, `answerable:true`, `expected_source_url`, `required_quote`) and unsupported examples (`question`, `answerable:false`). See [QA_EVALUATION.md](QA_EVALUATION.md). User rights and heldout status must be confirmed; it cannot prove they are true.

```powershell
py -3.12 -m neurogenesis.qa_baselines --db "C:\\private\\experiences.sqlite3" --audit "C:\\private\\independent-qa.jsonl" --confirm-corpus-rights --confirm-untouched
```

The aggregate JSON report never contains raw questions, URL strings, local paths, excerpts or private checkpoint data. The SQLite connection is read-only, there is no brain or model update, and both algorithms see the same newest source revisions. Any result is a **literal quote-attribution comparison**, not a factual truth or natural-language reasoning benchmark.

## Tests, limitations and next step

`tests/test_qa_baselines.py` uses fictional SQLite sources, changes one URL to a newer revision, and verifies the old version is absent; computes actual BM25 ranks, compares with current citations, includes a misleading unsupported premise sharing subject tokens, checks both engines' errors and ensures the original private DB SHA-256 remains unchanged. The dedicated offline `qa-acceptance.yml` exercises this beside the Wilson confidence gate.

These tiny public developer fixtures **cannot demonstrate independent real-world generalization**. For v1, run a new, unused, rights-cleared human QA collection, evaluate neural/source-grounded alternatives versus BM25 and abstain-all on identical criteria, require both good supported recall and low false-positive citation, and refuse any automatic promotion without explicit operator approval, checkpoint rollback and old-skill retention.

No current experimental checkpoint represents an AGI, a faithful biological human brain, verified factual understanding or a production natural-language model.
