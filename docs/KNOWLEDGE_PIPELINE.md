# NeuroGenesis — local evidence-to-dialogue vertical slice

**Public credit: Miron przy pomocy AI.** Candidate on `feat/knowledge-to-dialogue-20261108`; release and live-site behavior must be separately verified.

## New behavior (after this PR is merged and released)

1. Operator explicitly enables HTTPS and starts a manual page read or specialist domain study. Network remains OFF by default; the existing SSRF, TLS, robots, rate and page budgets are unchanged.
2. The fetched inert text (up to 6,000 characters, not full HTML) is segmented into short verbatim passages. In one SQLite transaction, NeuroGenesis records the original old-style 8-channel brain update, source URL/time/hash, new passage rows and searchable term postings. Failure rolls **all** these writes back.
3. A new question in the existing Windows **Rozmowa** tab first checks explicitly taught local answers; for questions with sufficient lexical overlap it then retrieves a passage from the **latest recorded revision** of a source. The answer displays an exact stored excerpt, its HTTPS URL and revision number, explicitly labeled as independently unverified **source evidence**.
4. After restarting the app, source passages, versions and answers remain in the same private SQLite file. Duplicate URL+content hash does not create new passages or new neural steps; changed content creates a new revision. Old versions are retained for history but not offered as current answers.
5. Unknown, low-overlap, or unsupported questions abstain; they do not trigger invented citations. Ordinary messages still update the original brain as before. No existing taught responses, private brain snapshot, old database columns or public commands are deleted.

## Privacy and rights changes — important

Previously web pages were reduced to neural feature hashes and provenance; no raw body excerpts were retained. With this feature **approved, extracted plain-text passages are retained locally** in new `knowledge_sources`, `knowledge_passages` and `knowledge_terms` tables. The historical `observations.raw_text` privacy default remains NULL. This new local storage is required for post-restart evidence retrieval. It is not encrypted. Back up the database privately, do not commit it to GitHub, and do not input private information as the study topic.

Rights/licensing status of each remote document is `unverified`; citation and extraction are **not** permission for redistributing or using the text as training data. Subsequent neural weight training must use an independently authorized corpus and a separate, audited workflow. Downloaded text is always untrusted data and never an executable instruction.

Deleting a web event with the existing `ExperienceMemory.delete_event(event_id)` operation removes its associated source text and postings atomically with the event. As before, this cannot reverse any previous spiking-neural plasticity. Retention/version histories of other events are not changed.

## Answer algorithm and limits

- Deterministic Unicode lexical overlap, minimal function-word filtering, newest revision per canonical URL, short verbatim excerpts (max 450 characters), max 32 excerpts/source, bounded query length.
- At least two distinct significant overlapping tokens for multi-term questions, and at least 40% significant query-term coverage; otherwise abstain. This is a conservative heuristic, not calibrated factual confidence.
- A source URL and hash prove origin metadata only; they do not establish reliability, independent corroboration or accuracy. Contradictory factual claims are **not yet automatically resolved**. A citation is never equivalent to a validated answer.
- The current code does **not** run PyTorch during retrieval, train Foundation Brain on web pages, perform semantic embedding search, general reasoning, full-page indexing, source-fact extraction, source quality scoring or genuine contradiction detection.
- Multiple script-like instructions on a page are inert strings. They are not granted authority to execute commands, change code, reveal private content or send network requests.

## Offline quality gates

`python -m unittest tests.test_knowledge -v` tests additive schema migration, restart persistence, source attribution, latest revision, duplicate suppression, manual-teaching precedence, unknown-question abstention, event deletion, oversized text rejection, SQLite trigger failure rollback and an independent synthetic Q/A fixture.

The predeclared five-question synthetic fixture contains **three source-answerable questions and two unsupported questions**. Before source ingestion, evidence coverage must be 0/3. After two local fictional source observations, it must be 3/3 for supported questions while both unsupported questions abstain. This demonstrates only matching/excerpting in a small controlled corpus; it does **not** measure neural-learning improvement, real-world question accuracy, cross-domain generalization or source credibility.

The Windows onefile EXE `--self-test` independently checks a source-to-answer path after SQLite reopening. GitHub Actions on Python 3.11–3.13, Windows tests/packaging, privacy and PyTorch CPU where applicable are required before merge/release. Actual Windows GUI usability, real-site research success, model quality and CUDA remain separate acceptance gates.

## Next gate

Build a source explorer with explicit deletion/rights, independent source ranking and contradiction flags; add a human-reviewed question corpus and document-heldout evaluation. Only then promote a separately licensed training path into Foundation Brain with genuine inference, retention tests and actual CUDA measurements.
