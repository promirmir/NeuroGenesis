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

## Later model-training candidate (requires explicit rights and action)

A separate later PR adds per-revision operator approval for local training, a rights audit table, and actual PyTorch Foundation Brain next-byte learning on eligible **latest** source documents with a whole document held out for validation. It never triggers automatically from browsing or citations, does not use unapproved documents, and produces only a private candidate checkpoint — not a trained conversational inference model. See [KNOWLEDGE_TRAIN.md](KNOWLEDGE_TRAIN.md). This is not part of the original PR #27 release until separately tested and merged.

## Next gate

Build a source explorer with explicit deletion/rights, independent source ranking and contradiction flags; add a human-reviewed question corpus and document-heldout evaluation. Only then promote a separately licensed training path into Foundation Brain with genuine inference, retention tests and actual CUDA measurements.

## Two-host evidence review (later PR candidate)

A new backward-compatible retrieval pass can return a second **short verbatim quotation** from a different hostname in the most recent retained URL version, with its own SHA-256 URL/version metadata. It optionally flags **potential** numeric or explicit negation differences between the two extracts; these are merely review triggers with false-positive potential. The system never concludes the sources objectively contradict, prove truth, are independently authored or license each other's reuse. Manual teachings remain first. Unknown questions abstain, prior SQLite state/teaching is retained, and the old `source` field stays valid. Offline tests verify same-host exclusion, superseded revisions and synthetic conflicting excerpts. This functionality is a candidate until merged and passed Windows EXE and Python/Qt CI.

## Conservative contextual follow-ups (later PR candidate)

The optional Qt chat service may hold the prior **grounded** question and its selected source URL *in memory only for this session*. If the next message explicitly begins with `A/I/Or az ...?` and contains fresh substantive tokens, those terms may be searched alongside the previous topic; a returned quotation must belong to the **same exact prior URL's latest revision** and contain new focus terms. Otherwise the app abstains. User input is still passed to the unchanged sensory memory, not replaced by the expanded retrieval text, and no raw session transcript is saved in SQLite by this feature.

This is deterministic lexical context restriction, **not learned coreference or true language understanding**. The operator can clear the transient topic without affecting prior brain, teachings or knowledge. Manual teachings always have precedence. Tests check missing focus, cross-host evidence exclusion, revision supersession, restart, SQLite privacy, Qt status and clear action. Candidate subject to CI before release.

## Exact quote/source QA audit (later PR candidate)

`neurogenesis.qa_eval` can now score a rights-cleared *locally held-out* `.jsonl` question list against the current **read-only** versioned knowledge store. It checks whether the actually returned inert excerpt includes a specified literal answer span AND is linked to the specified source URL; it separately measures false citations for unsupported questions, abstention and latency. `quoted_evidence` binds source URL to quotation inside the existing retrieval result; this is additive, never synthetic text. No SQLite write, Internet access, model inference, stored audit question or raw per-question logs occur. Corpus rights and independence must be explicitly confirmed. See [QA_EVALUATION.md](QA_EVALUATION.md). Synthetic smoke metrics are not real-world semantic correctness evidence.

## Verified source-review and contextual dialogue follow-up (PR #36–#38)

PR #36 merged to main `0bcfb6a158c57465b0b39dda26e4ed3ca20e22bd`, #37 `c94dce00761d938e12215b19c20dbfd9efe426a9`, and #38 `4a81cc76a3191ee4031e8bfde9430626a50914ad`. Verified PR CI: Python 3.11–3.13, actual Torch CPU, privacy, actual Qt Windows/Ubuntu and frozen original Windows Tk EXE (plus technical Qt frozen smoke where applicable). Multiple snippets remain untrusted, different hostnames are not independent fact proof, contextual followups are session-only strict same-URL/novel-focus matching, and the QA evaluator measures literal URL/excerpt retrieval rather than semantic accuracy. Tiny fictional evaluation found one false citation for three unsupported queries; fix must be proven against **fresh holdouts**. Historical candidate sections above are superseded.
