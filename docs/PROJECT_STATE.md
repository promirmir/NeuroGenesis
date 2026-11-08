## 2026-11-08 — verified cited-dialogue quality milestones after PR #38

- **Source main:** `4a81cc76a3191ee4031e8bfde9430626a50914ad`. PR #36 `0bcfb6a158c57465b0b39dda26e4ed3ca20e22bd`, #37 `c94dce00761d938e12215b19c20dbfd9efe426a9`, #38 `4a81cc76a3191ee4031e8bfde9430626a50914ad` are **merged**. No open implementation PR at this checkpoint. Historical "PR candidate" sections below document past work, not current state.
- **#36**: newest URL revision and lexical source matching now display up to two bounded literal excerpts from different **hostnames**, real URL/SHA/version provenance and only **possible** numeric/negation discrepancies requiring human review. Different hostnames are not independent fact checking, and snippets are never executable instructions. Existing taught response priority and private SQLite remain.
- **#37**: optional Qt conversation can keep an **ephemeral**, in-process last grounded topic and exact source URL. Explicit Polish `A...?` follow-ups must have a substantive new focus term in an excerpt from the **same source's current version**. Unsupported context abstains. Raw conversational context is not saved to SQLite; clear-context does not delete existing knowledge. This is lexical carryover, NOT general neural language understanding.
- **#38**: independent read-only `neurogenesis.qa_eval` accepts operator-owned/heldout local JSONL questions (answerable cases with exact expected URL + quote, unsupported cases), requires explicit rights/holdout confirmations and reports only aggregate citation/abstention and retrieval latency metrics. No network, training, brain mutation, or raw question logs. Synthetic smoke in Python 3.12 GitHub CI: **3/3 expected literal citations; 2/3 correct abstentions; 1/3 unsupported queries incorrectly received source citations; overall 5/6=83.33%**. Actual p95 SQLite-only retrieval latency `0.33562 ms` on that CI runner. This test is *fictional and tiny*, NOT semantic factual accuracy, cross-domain generalization or robust neural model competence.
- Final feature PR #38 head `e8511d1f34e6fde98be607c170c72186c0335b50` passed Python 3.11–3.13, real PyTorch CPU, privacy, Qt Windows/Ubuntu and legacy frozen Tk Windows EXE before squash merge. Post-merge main CI and any new EXE release still require independent confirmation.
- Official downloadable Windows Tk EXE remains separate from optional, technically tested but legally gated **Qt Command Center** redistributable. No live CUDA GPU measurement, no independent rights-cleared human Q/A run, no validated long-context neural chat, no v1 or AGI claim.
- **Highest next gate:** reduce unsupported **false citations** without tuning against the same tiny fixture; prepare an unused licensed QA audit set and compare coverage/abstention tradeoffs. Next: calibrated factual/semantic model evaluation versus strong baselines, versioned memory rollback, physical GPU benchmark, Qt licensing and installer. See [docs/QA_EVALUATION.md](QA_EVALUATION.md), [docs/KNOWLEDGE_PIPELINE.md](KNOWLEDGE_PIPELINE.md), [docs/RETENTION_GATE.md](RETENTION_GATE.md).

## 2026-11-08 — offline grounded QA quality measurement (PR candidate)

- `main` baseline `c94dce00761d938e12215b19c20dbfd9efe426a9`, PR #37 merged after Python 3.11–3.13, actual Torch CPU, Qt Windows/Ubuntu, frozen Tk and Qt technical EXE checks green. It adds strictly **session-only lexical context** to optional Qt, no neural semantic understanding claim.
- Branch `feat/offline-grounded-qa-benchmark-20261108` implements an opt-in `neurogenesis.qa_eval` CLI with a bounded local **held-out** question+literal citation JSONL, operator-declared data rights and independence. It evaluates actual newest-revision SQLite quoted text to exact expected URLs and literal spans; separate supported recall, source attribution, false citation/abstention, and p50/p95 retrieval latency. SQLite opened **read-only**, no persisted questions, brain updates, network or raw private audit data in reports.
- Mandatory synthetic fixture intentionally includes a lexically overlapping unsupported question to expose rather than conceal false answer risk. This is evidence matching only, not semantic/factual QA or neural inference. Tests additionally cover exact source excerpts, consent, invalid data, no SQLite mutation and privacy.
- Candidate pending Python 3.11–3.13, real Torch CPU, Windows Tk EXE, privacy and Qt checks. See [QA_EVALUATION.md](QA_EVALUATION.md).

## 2026-11-08 — conservative source-grounded short follow-ups (PR candidate)

- Current `main` at feature start `0bcfb6a158c57465b0b39dda26e4ed3ca20e22bd`, PR #36 **merged** with Python 3.11–3.13, real PyTorch CPU, privacy, Qt Windows/Ubuntu and frozen Tk Windows EXE checks green. Its two-host source comparison warns only about **possible** text/numeric discrepancies; factual accuracy and publisher independence remain unverified.
- Branch `feat/session-grounded-followups-20261108` adds **session-only** (memory-only, not SQLite) previous sourced question and URL in `CommandService`. Explicit short follow-up question beginning `A/I/Or az ...?` is re-evaluated using last topic and only the exact prior source URL, requiring a new substantive term actually present in a latest-version excerpt. No topic/no relevant new evidence => normal abstention. `Clear context` in Qt removes the volatile topic without deleting private SQLite records; exact manually taught answer continues to win.
- Tests cover actual SQLite after restart, source version replacement, cross-host refusal, manual teaching precedence, no private raw question storage, explicit invalid queries, and Qt session state. Tk `process_message` defaults unchanged. **Candidate pending full Python 3.11–3.13, privacy, actual Qt Windows+Ubuntu, and frozen legacy Windows EXE.** No LLM coreference or semantic reasoning asserted.

## 2026-11-08 — multi-source evidence review / discrepancy flags (PR candidate)

- Starting verified main `200a78cbe7e60777a9fc6a368268c6a055b74c4d`, PR #35 was merged; source-based chat remains primary and can show one verbatim excerpt; independent natural-language model quality is unverified.
- Branch `feat/evidence-review-multi-source-20261108` expands local newest-revision retrieval to show up to **two bounded verbatim extracts** from different hostnames with exact URL/version/SHA metadata. Both are independently unverified; different hostnames are NOT proof of independent authors or factual corroboration.
- Conservative **possible** numeric and negation divergence signals trigger manual-review notice, not asserted factual contradictions or fabricated synthesis. Preserve manual-teaching priority, legacy first `source` field, SQL transaction/privacy behavior and source abstention. Qt/Tk receive both provenance entries through unchanged chat response.
- Synthetic no-network tests explicitly check two-host reporting, numeric/negation flags, revision supersession, same-host exclusion, low-overlap abstention and private SQLite after restart. **Candidate until full Python 3.11–3.13, Windows standalone EXE, Qt Windows/Ubuntu and privacy checks pass.** No automatic factual verification, AI understanding or neural training claim.

## 2026-11-08 — verified neural learning/inference/retention milestones (#32–#34)

- Current functional main SHA `6a45379c2310bc0622b932e21406feddbdbdcd4d`. PR #32 (`ec5bc9fcfdbc2fa7c940e33fc8b090a48ed610b7`), #33 (`fd4ab6a723baad237d583d62991dbfdcd84b3f74`) and #34 (`6a45379c2310bc0622b932e21406feddbdbdcd4d`) **merged**. Historical sections marked "candidate" below refer to their past, unverified development states.
- Actual Foundation PyTorch multiscale GRU **can now infer** bounded next UTF-8 bytes from an explicitly trusted local trained checkpoint in an independent Qt inference lab (#32). Not a sourced chat response, natural-language understanding or credible fact.
- Candidate comparison on distinct operator-supplied old/new audit documents (#33) is actual CPU PyTorch and evaluates old-skill retention and new-task improvement. Its fictional benchmark **failed the 1% new-improvement gate**: old CE `5.7167409→5.6910159`; new CE `5.7461666→5.7415593` nats (~0.08% gain). No checkpoint promoted.
- Controlled two-stage learning (#34) now resumes true trained numerical weights from explicit trusted .pt, writes a separate new checkpoint, and preserves SHA-256 of previous weights. Synthetic CPU test ran 2+2 optimizer steps (cumulative 4) and measured holdout next-byte CE `5.6478154→5.5607319` nats; **still not better than Markov**. AdamW optimizer moments are NOT resumed and training starts a fresh optimizer each session.
- On the final PR #34 source head `4e3199089421942a42a6d30ffa3a890e1f7b0abf`, all Python 3.11–3.13, privacy, real CPU PyTorch, Qt Windows/Ubuntu, legacy Tk frozen Windows EXE and separate Qt frozen EXE quality gates passed before merge. The *post-merge main* release must be checked independently. No physical CUDA hardware benchmark or independent natural QA corpus run.
- Public Tk EXE still uses local SQLite source retrieval for cited answers. Qt Command Center and PyTorch remain optional source/technical CI builds; **no compliant downloadable Qt bundle** has been published. Next critical milestones: independent licensed QA and source truth evaluation, actual semantic neural conversational performance vs strong baselines, safe candidate acceptance/rollback, measured CUDA hardware test and Qt redistribution compliance. See [docs/FOUNDATION_INFERENCE.md](FOUNDATION_INFERENCE.md), [docs/RETENTION_GATE.md](RETENTION_GATE.md), [docs/KNOWLEDGE_TRAIN.md](KNOWLEDGE_TRAIN.md).

## 2026-11-08 — safe continued Foundation training weights (PR candidate)

- PR #32 merged `ec5bc9fcfdbc2fa7c940e33fc8b090a48ed610b7`; PR #33 merged `fd4ab6a723baad237d583d62991dbfdcd84b3f74`. PR #33 passed Python 3.11–3.13, actual PyTorch CPU, privacy and Windows Tk frozen EXE. Its synthetic paired old/new test **rejected** the candidate because improvement on the new task was below 1% threshold, preserving scientific integrity. Qt was unchanged in PR #33.
- New branch `feat/safe-foundation-continue-learning-20261108`: controlled continuation from an operator-trusted local checkpoint, preserving prior weights and adding real Torch gradient steps. Generates **a new checkpoint without overwriting the previous file**; model architecture must match, rights for current source versions confirmed, and optimizer moments are **not** persisted (fresh AdamW). Qt Training UI exposes explicit opt-in. Tests cover actual CPU weight/step continuation, source hash preservation, no overwrite, trust failure, architecture mismatch and service worker.
- Candidate pending Python, PyTorch CPU, Qt Windows/Ubuntu, frozen original Tk EXE and Qt EXE quality gates. No independent semantic chat, automatic model promotion, real CUDA benchmark or redistributable Qt download claimed. Read `docs/KNOWLEDGE_TRAIN.md`, `docs/RETENTION_GATE.md`.

## 2026-11-08 — old-skill/new-task paired checkpoint audit candidate

- `main` advanced to `ec5bc9fcfdbc2fa7c940e33fc8b090a48ed610b7` by merging PR #32 after real PyTorch CPU, Python 3.11–3.13, Qt Windows/Ubuntu, Windows Tk frozen EXE, Qt frozen EXE and privacy checks. It adds an operator-trusted, offline actual Foundation checkpoint inference **laboratory**, never automatically used as chat or a factual source. Prior candidate notes below are historical.
- Branch `feat/foundation-candidate-retention-audit-20261108` adds `foundation_gate.py`: actual paired checkpoint CE on two different operator-supplied old/new audit text files, numeric regression and new-task improvement gates, explicit trusted/checkpoint and corpus permission, fixed comparable model architecture, zero automatic promotion. Separate real CPU tests and CI metric emission. See [RETENTION_GATE.md](RETENTION_GATE.md).
- This remains a **candidate pending CI**. A numeric old/new task pass will not establish model-based contextual chat, prevent future forgetting in all domains, or prove datasets were unseen. CUDA hardware and Qt legal release remain open.

## 2026-11-08 — isolated trained-checkpoint inference (PR candidate)

- Reverified baseline main `0afcb2b37ee908c4810b6c545e8833ebef9fd787`, no open PR, last main CI/Windows release successful. Current branch `feat/foundation-inference-lab-20261108` implements a separate, **actual PyTorch GRU checkpoint decoding path** (not automatically connected to default chat).
- `neurogenesis/foundation_infer.py` loads an explicitly trusted trained local .pt/.pth with weights-only loader, performs deterministic greedy next-byte inference with real logits, max 64 generated bytes and sliding bounded context, and reports literal hex/UTF-8 plus measured bytes/s. It never writes SQLite, downloads models or claims cited facts. Invalid UTF-8 can occur, not meaningful language guaranteed.
- Optional Qt Training page gains an **isolated inference laboratory** and trusted-local-file picker; backend worker uses real weights, bounded queue/events and cancellation; default Tk EXE unchanged. New real CPU tests validate checkpoint logits, deterministic restart, consent, limits, no private-memory writes, async service. See [FOUNDATION_INFERENCE.md](FOUNDATION_INFERENCE.md).
- Candidate must pass Python 3.11–3.13, real PyTorch CPU, Qt offscreen Windows/Ubuntu, both Windows frozen EXE checks and privacy before merge; no claimed semantic generation, AGI, CUDA measurement or Qt redistributable release.

## 2026-11-08 — verified milestone after PR #30 merge

- Current functional integration commit: `334b1afc842f662b422b8ca81404c3fd75874523` on `main`, with PRs #23, #27, #28, #29 and #30 **merged**. No open implementation PR left from this batch.
- #27: opt-in public HTTPS evidence → atomic private SQLite passages/version ledger → quoted URLs in existing chat after restart, with lexical retrieval (not Torch weight learning).
- #28: separate usable PySide6 dark Command Center over true SQLite/chat/research/brain/sources; #29: actual Windows Qt frozen onedir executable built and smoke-tested via CI, but **not uploaded/released** pending Qt LGPL third-party notice and packaging compliance.
- #30: separately operator-approved latest source revisions → actual PyTorch Foundation Brain candidate-gradient training and independently held-out **whole-document** evaluation; Markov baseline, real progress/cancel, CPU/CUDA selection and Qt controls. Chat still uses sourced extracts, **not neural model inference**.
- Final feature-PR CI green across Python 3.11–3.13, privacy, actual PyTorch CPU, Qt offscreen Windows/Ubuntu, existing frozen Tk EXE and optional actual frozen Qt EXE. Controlled synthetic CPU fixture after **3 optimizer steps**: held-out byte CE `5.7385942 → 5.5994536` nats (about 2.42% relative improvement), against a **better** first-order Markov baseline `1.7341138` nats. This is real weight learning on tiny synthetic data, not useful general language competence.
- Qt DLL bundle is about 112 MiB, not a released installer; CUDA hardware, independent real-language accuracy/retention, rights verification and manual Windows DPI tests remain unverified. Do not claim AGI, self-awareness, training on unrestricted internet or a completed v1.
- Continue only from current main and [KNOWLEDGE_TRAIN.md](KNOWLEDGE_TRAIN.md)/[COMMAND_CENTER.md](COMMAND_CENTER.md). Highest next acceptance gate: evidence-grounded neural inference with independent corpus and forgetting tests, then legally compliant Qt packaging and stabilization.

## 2026-11-08 — Rights-approved web evidence → actual PyTorch training (PR candidate)

- PR #29 verified and merged to main `9388e19356c2d7f49ffdd1a72d0996d3d89986b0`: Windows frozen Qt EXE `--self-test` passed actual GUI/SQLite sourced chat, packaged dynamic DLLs, EXE SHA-256 `2d563058b985f169ae04b39f8674f1f5d2a5fc85af0dbfc6d32b86c3501ac3b8`, bundle 111.95 MiB. **Not released/uploaded pending Qt LGPL distribution audit**, old Tk EXE remains released.
- Feature branch `feat/approved-web-foundation-train-20261108`: explicit per-source/revision local rights approvals with audit trail; only latest approved versions eligible; `neurogenesis/knowledge_train.py` invokes actual Foundation Brain Torch byte-prediction gradient training after a second explicit corpus-rights confirmation. Whole document held out from train, real before/after cross-entropy and Markov baseline, measured step/s, CUDA VRAM only on actual device, atomic **candidate** checkpoint and cancellation. No automatic trainer on web fetch, no trained model chat inference or independently validated semantics. Qt now presents rights controls and bounded training progress.
- `tests/test_knowledge_training.py` includes real CPU Torch, source-rights/revocation/revision, cancellation and numeric evaluation. Dedicated real PyTorch CI trigger expanded, standard Python and Windows Qt/Tk gates preserved. Candidate source and tests are **not yet CI verified or merged**. Details [docs/KNOWLEDGE_TRAIN.md](KNOWLEDGE_TRAIN.md).

## 2026-11-08 — Windows Qt EXE technical smoke candidate (not a release)

- PR #28 **merged** to main `2bd5af5a1db70dee8566f848a41d5024e8fa8bba` after actual Qt offscreen Windows and Ubuntu checks, real PyTorch CPU, Python 3.11–3.13, Windows frozen original Tk EXE and privacy gates all passed. Qt Command Center source GUI is implemented, but **no Qt EXE has been released**.
- Branch `ci/qt-windows-frozen-smoke-20261108` adds a separate optional Qt launcher, local temporary-SQLite evidence/chat `--self-test` and a Windows `--onedir` PyInstaller technical-only workflow that must run the actual Qt EXE, verify dynamically linked DLLs, SHA256 and package size. Does **not** publish a redistributable bundle before license and packaging audit. See `docs/COMMAND_CENTER.md`. Await CI.

## 2026-11-08 — Actual Qt Command Center candidate (PR pending)

- PR #27 merged to main `a284aae07934fee42db55897a8cde4eb3312713e` after successful Python 3.11–3.13 and Windows standalone EXE/priva­cy checks. This implements local sourced **lexical** responses but not neural weight learning. Final release publication must be independently checked.
- New branch `feat/command-center-qt-service-20261108`: real optional PySide6 application + Qt-independent `CommandService` consuming the same SQLite, cited chat, bounded specialist research, real brain traces, versioned source browser, system state and explicit network permission. Default Tk EXE/SQLite retained.
- Dedicated `qt-command-center.yml` tests actual Qt widgets offscreen on Windows and Ubuntu; service tests prove persistence, revision access and no-network/revocation. Qt Python dependency opt-in only; no release claim until CI and packaging/licensing proof. No GPU, Foundation model training, factual verification or independent live-web success measured.
- Continue in `docs/COMMAND_CENTER.md`; do not confuse this functional source preview with a verified Windows Qt EXE.

## 2026-11-08 — PR #27: private source evidence → Windows dialogue (candidate)

- PR #23 was merged into main commit `66f3d61fa1696aaeeb3c33c0d035100a9aaacba1` after Python 3.11–3.13, real PyTorch CPU, Windows standalone EXE and privacy checks passed. Historical notes below that called PR #23 open were written earlier.
- PR #27 `feat/knowledge-to-dialogue-20261108` implements the first *retrieval-based* end-to-end web→local passages→cited Windows chat slice. Approved extracted text (up to 6,000 characters) is now kept privately in additive SQLite tables in the original atomic neural/provenance transaction. Exact manual teachings retain precedence, changed URL content is versioned, duplicate material is skipped, and unsupported questions abstain.
- Existing `observations.raw_text` stays NULL by default and old SQLite/brain APIs are preserved. Foundation Brain weights are **not** trained and source truth is **not** independently validated. See `docs/KNOWLEDGE_PIPELINE.md` for licensing/privacy and `docs/COMMAND_CENTER.md` for the planned Qt architecture (not yet implemented).
- First CI run `42465142616`: all 11 new knowledge tests passed, but one pre-existing taught-response wording regression failed. Restored exact legacy phrase in source commit `d4fc8fe2a2b3ec2a5e0e06d70fbac96af4a417b3`. Fresh full Python/Windows/EXE and privacy CI still required before merge/release; zero CUDA or real-site benchmark claimed.

## 2026-11-08 — Delivery audit and UI completion requirements

- Audited current main `db0b2210bb97c422d83d27f963725d3d6941c067` and release `v0.6.0-main.db0b2210`. Source: [docs/DELIVERY_AUDIT.md](DELIVERY_AUDIT.md). No independent Windows screenshot/manual usability audit or real-site crawl benchmark was performed; GitHub Actions validated Python regression, frozen EXE smoke and release checks.
- Critical gap: web text flows to legacy 8-channel LIF memory, not a persistent semantic knowledge store or Foundation Brain weight-training/chat inference. The PyTorch model remains a separate, trainable research module; exact taught Q/A is not autonomous language understanding.
- Next coordinated P0: end-to-end source evidence → persistent knowledge → grounded response and measured held-out questions, alongside professional responsive Windows dashboard/conversation/research/training UI without backend regressions.
- Outstanding PR #23 must be evaluated against its current base and test gates; green Linux foundation CI alone does not prove the Windows gate for that PR.

## 2026-11-08 — Multi-domain specialist research, PR #24 MERGED

- Expanded beyond static Wikipedia seeds: safe HTML anchor extraction, topic-filtered BFS across public HTTPS domains, robots.txt policy, crawl-delay, 500-attempt upper budget, 50 domains, 20 attempts/host, depth 3, 600 URL queue, >=5 seconds between page fetches. GUI default 120 attempts and displays domain/discovery/error counts. Existing Internet opt-in controls all network access.
- Manual page reader retains 128 KiB limit; explicit crawler mode has a separately bounded 512 KiB limit. HTML text is capped at 6000 chars and URLs are revalidated through pinned TLS/public IP checks. No unrestricted entire-internet indexing, search API, forum guarantees, semantic understanding or PyTorch gradient training.
- New offline tests validate robots transport, denied paths, failed robots reads, cross-domain discovery, URL filtering, content size, stop and consent. Latest code and Windows tests must be verified on final branch head before any merge/release.
- PR #24 source head `c90126532de97189d3717b4adabb25d71a0b55fe` passed Python 3.11–3.13, source/privacy audit and Windows EXE build/smoke. Squash merged to `main` commit `578222800c5adc73c0a756352b5bef405535252a`. Main Python CI (run 42463459779), Windows standalone EXE build/smoke (run 42463459963) and release publishing (run 42463541158) all succeeded. Verified GitHub release `v0.6.0-main.57822280` targets `578222800c5adc73c0a756352b5bef405535252a` and contains `NeuroGenesis.exe` plus SHA-256. The executable asset digest is `20708872a4c2b35484da100a88794aaef321e329d469524eb63162b4638b4731`. No production real-site research benchmark has yet been verified. See [docs/SPECIALIST_STUDY.md](SPECIALIST_STUDY.md). PR #23 remains separate and open.

## 2026-11-08 — Historical initial PR #24 candidate (subsequently merged)

- The original bounded Wikipedia-only candidate has since been expanded in the above PR #24 milestone to multi-domain link discovery. Retained historical note: GUI-thread SQLite persistence and network-off-by-default.
- No full-Internet indexing, general search API, trained language model, or demonstrated expertise. Follow latest PR #24 details above and `docs/SPECIALIST_STUDY.md`.
- Historical initial source commit: `44e579c71335f6ae02d568aaba99244bb81280dd`; final merged commit is `578222800c5adc73c0a756352b5bef405535252a`. PR #23 remains independent.

# NeuroGenesis — durable project state and recovery

## 2026-11-08 — PR #23 conflict resolution candidate (not yet validated)

- The original CI coverage PR #23 was behind main and conflicted on durable docs; its first head had passing Python 3.11/3.12/3.13 and real PyTorch CPU tests, but lacked the Windows EXE run because the existing Windows workflow pull-request path filter did not select foundation workflow changes.
- Resolved the candidate against main `542ba8272ceb4c0c13871b9f9fd954c23d4c4cdb` on the original PR branch; dedicated PyTorch CI pull_request paths now include the byte-baseline module/test, the CPU job explicitly runs baseline tests, and Windows EXE PR path filters include changes to foundation-cpu.yml. Preserves all runtime/SQLite state; no model or user data changes.
- Do NOT merge until new branch head has successful Python 3.11–3.13, real PyTorch CPU, Windows standalone EXE and privacy test results. This note describes candidate source, not delivered functionality.


Last documentation review: **2026-11-07**. This file is intended to survive chat interruptions and model/context changes.

## 2026-11-07 — Permanent mission and current v0.6.0 web-sense candidate

- Primary, durable specification: [docs/VISION.md](VISION.md). Build a genuinely capable learned, scalable neural AI with GPU/compute expansion, lifelong learning, private long-term memory, grounded public Internet sensing, useful Polish Windows chat, realtime brain/learning telemetry, and falsifiable neurobiological mechanisms. This is a scientific aspiration, not proof of a breakthrough.
- **PR #19 merged** the genuinely trainable optional PyTorch multi-timescale Foundation Brain in main commit `96d3e04b126712aa6a33029b80ed5bbe7ca20af7`. Dedicated real PyTorch CPU tests, Python 3.11–3.13, and Windows standalone regression/executable smoke all passed. The new model is not yet trained for semantic dialogue and is NOT active in the default EXE.
- **v0.6.0 candidate** adds pinned HTTPS public-text perception in a user-enabled Internet tab. Worker reads max 128 KiB of plain/html, rejects private/DNS-rebinding addresses, redirect and credentials, extracts up to 6,000 chars, persists source URL/UTC/SHA256 with neural brain data atomically. Optional repeat checks only the manually approved URL every 5 minutes. Network OFF by default and no raw downloaded body is kept in SQLite.
- GUI Mózg graph and statistics update automatically every three seconds. Source text is treated as untrusted observation, not commands. No semantic learning or verified language-world model is claimed.
- **Release gate:** this candidate requires all original Linux/Windows CI tests, dedicated Foundation CI, real SQLite web integration and frozen EXE smoke tests before merge and GitHub Release. Until verified, users should download the latest validated v0.5.6 release.

## 2026-11-07 — High-capacity Foundation Brain pivot (issue #18)

- The user rejected the scientific and practical scale of earlier 24-neuron / 8-channel demonstrations. Those experiments are retained as baselines only; do not advertise them as a path to competitive language understanding.
- PR #17 (eight-bin temporal prediction) is **closed without merge**, its feature branch retained for controls. Verified v0.5.6 remains the default Windows EXE; old SQLite schema must not change.
- New research branch must implement a **trainable neural foundation** using ordered symbol representations, fast/slow context, gradient-trained predictive objectives, versioned checkpoints, optional PyTorch/CUDA and dedicated real dependency CI. See docs/FOUNDATION_BRAIN.md.
- No human-like semantic understanding, long-term reasoning, GPU performance gain or general intelligence has been demonstrated by this architecture. Train on permissioned data and run independent, matched compute baselines first.
- Separate foundation CPU CI must be green before merging; when merged, default Windows EXE remains unchanged. Later GUI inference requires actual usable trained weights and authorized local worker resource controls.

## Distribution — permanent latest Windows EXE link

- Public entrypoint: [GitHub Releases — latest](https://github.com/promirmir/NeuroGenesis/releases/latest); direct asset: [NeuroGenesis.exe](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe); [SHA-256](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256).
- Trusted `.github/workflows/publish-release.yml` runs only after a green, main-branch Windows standalone EXE build. It downloads the successful build artifact, rechecks its SHA-256 and PE x64 format, validates the main source SHA, and publishes an immutable SHA-tagged release with a separate **contents:write** permission. PRs retain read-only permissions.
- **Verified publication:** GitHub Release v0.5.5-main.bb7b6282 was published on 2026-11-07 with both NeuroGenesis.exe and its SHA-256 (successful release run 42419193604). The stable latest/download link resolves to an actual asset. Later version changes must pass independent CI and create another verified release.

## v0.5.6 candidate — explicitly teachable local responses

- New SQLite associations let the operator teach, correct and delete up to 512 exact normalized question–answer mappings. Teaching and the existing neural sensory path are atomic, but language response text is retrieved from the separately identified symbolic association table, NOT generated by the spiking brain. Normal observations remain text-private by default.
- Native Tk GUI adds a second text field and Teach/Delete controls. EXE self-test and new integration tests cover restart persistence, question normalization, fail-closed corruption, privacy, old message length compatibility and no divergence of the autonomic predictor. See docs/TEACHABLE_DIALOGUE.md.
- This is a candidate until CI and Windows EXE build pass and the PR is merged. Do not call it verified on main prematurely. The existing released baseline is v0.5.5.

## Verified main v0.5.5 — bounded opt-in local self-development

- New neurogenesis/autonomy.py adds an opt-in supervisor using **the same private SQLite brain** as the native Windows app. Every 40 fresh observations are assigned once to separate guard/training/selection/audit roles.
- Successful *measured* candidate adaptation persists the associated trained neural readout and underlying spiking brain atomically to SQLite, with audit record, checkpoint and rollback allowed only before intervening new learning. Rejected candidates preserve the original brain.
- Existing v0.4/v0.5.4 memory files remain compatible; no internet, code-writing, GPU or automatic use of third-party machines. AUTO is OFF by default and only checks while the app is open. See docs/AUTONOMY_SUPERVISOR.md.
- This is a bounded local self-tuning mechanism, **not evidence of autonomous general cognitive development or human-brain equivalence**. Independent OOD and resource/retention benchmarks remain open.
- **Merged PR #12**, main merge commit bbd9c00c557a2e87621cf81c598195109f8e7716. All three Linux CI Python versions and Windows full tests and standalone EXE smoke test passed before merge. Verify fresh main runs before distributing the latest EXE. A follow-up hardening test explicitly refuses databases that contain experiences but lack a neural snapshot.

## Current verified main: v0.5.4 (2026-11-07)

- Merged [PR #10](https://github.com/promirmir/NeuroGenesis/pull/10): code landing commit `ddf6d3aa9c878c6f2ec221289521cf00349f8cba`. This identifier is a historical checkpoint, not a promise that latest `main` will never change.
- **GitHub verified** Linux `research-core-ci` on Python 3.11, 3.12 and 3.13, including original and newly added tests; Windows workflow passed **125 tests** and the PyInstaller onefile EXE runtime `--self-test` with actual SQLite. After merge, main Linux run `42414996746` succeeded and main Windows run `42414996678` succeeded, publishing the downloadable `NeuroGenesis-Windows-x64` artifact (14-day retention).
- `desktop_launcher.py` / `neurogenesis/desktop.py` implement the first native Polish Tkinter app. `%LOCALAPPDATA%\\NeuroGenesis\\experiences.sqlite3` stores local observations and brain state. Internet OFF. No ordinary conversational understanding is claimed.
- Bounded add-on research modules: `homeostasis.py`, `repair.py`, `fingerprint_repair.py`, `self_development.py`, `capacity.py`, `controls.py`, `skill_recovery.py` and `lesion_benchmark.py`. These are **offline experimental modules**, not an autonomous background supervisor, GPU backend or general-intelligence agent.
- Negative research results remain important: previous structural growth was not better than fixed topology on A-B-A; a non-neural Markov predictor greatly outperformed the neural predictor on one simple task. Capacity self-scaling rejected 10/10 proposed expansions when gains were absent. Repair improves task MSE on some narrow synthetic patterns but not on disjoint-cue transfer.
- Public identity policy: credit `Miron przy pomocy AI`; author/committer display names must exclude surnames; the operator accepted visibility of Git metadata emails. Issue #6 closed; continue scanning source and commit names for private information, do not force-rewrite Git history.
- Next milestones: continuous transactional self-development supervisor with real independent holdouts and rollback (#8/#9); safe opt-in read-only internet perception (#4); grounded language (#5) without false cognition claims; independent OOD validation (#3) and structural repair (#7). The Windows EXE must remain one-click and private-by-default.

## Mission

Develop an experimental, self-reorganizing neural substrate that learns over time, later links to controlled internet observations and text dialogue, retains its experiences and can report a calibrated, functional model of its own computational state. Scientific evidence is required for claims of capability. Subjective consciousness is neither currently implemented nor established by a test.

Public project credit: **Miron przy pomocy AI** (first name only). Canonical executable source: `neurogenesis/origin.py` (see `docs/ORIGIN_AND_OPERATOR.md`). Human governance and truthful acknowledgement are design commitments, not implemented authenticated command handling or real feelings.

## Verified implementation and limits

- **v0.4.0 reconstructed baseline** (v0.2 plus project origin/continuity): bounded sparse spiking LIF neurons; STDP-like local plasticity; novelty-triggered bounded growth; weak-synapse pruning; JSON checkpoint deterministic restart; offline text feature hashing (not semantics); observable telemetry.
- Online next-input predictor trained by prediction error, tested on a toy alternating sequence; growth did **not** outperform fixed structure. Reproduce with `python -m neurogenesis predict --steps 600`.
- `python -m neurogenesis compare --steps 128` tests growth/fixed structure under identical inputs (structural metric only).
- `python -m neurogenesis origin` shows canonical attribution and mission. New snapshots include origin metadata; old v0.2 and v0.2.1 snapshots load and upgrade to short attribution on next save.
- **Not built:** autonomous natural language reasoning, real web access, self-updating source, authenticated operator controls, verified subjective consciousness, GPU implementation. Do not silently claim otherwise.

## Continual-learning benchmark v0.3

A -> B -> A synthetic sensory association experiment uses 10 seeds, frozen
readout during independent noisy probes, and paired comparisons of growing and
fixed-structure substrates (not parameter/compute matched). On the local
10-seed run (128 steps/phase, 48-step probes, noise amplitude 0.15), A MSE
after B was **0.14877 (growth)** vs **0.14565 (fixed)**. The lower score for
the fixed architecture means growth did not improve retention. Benchmark results
are preliminary, from a narrow synthetic pattern family; do not generalize.

## Persistent memory v0.4

The `remember` command now saves hashed sensory features + corresponding
spiking brain state atomically in one local SQLite DB, with exact/fuzzy
feature recall and explicit opt-in raw text persistence. `forget-event` only
deletes its log record; it does not reverse learned synaptic state. No semantic
memory or language understanding is claimed. Memory data is not committed to
GitHub: *.sqlite3 and local-data/ are excluded by .gitignore.

## Reproduction from a clean checkout

```bash
git clone https://github.com/promirmir/NeuroGenesis.git
cd NeuroGenesis
python -m unittest discover -s tests -v
python -m neurogenesis compare --steps 128
python -m neurogenesis predict --steps 600
python -m neurogenesis benchmark --seeds 10 --steps-per-phase 128 --probe-steps 48
python -m neurogenesis origin
python -m neurogenesis remember "Pierwsza obserwacja" --db local-data/experiences.sqlite3
python -m neurogenesis recall "Pierwsza obserwacja" --db local-data/experiences.sqlite3
python -m neurogenesis demo --steps 64 --state brain.snapshot.json
python -m neurogenesis status --state brain.snapshot.json
```

Python >=3.11, no third-party dependencies, runs offline on CPU. GitHub Actions executes test jobs on 3.11/3.12/3.13.

## Progress / future work

- Reconstructed v0.1 and v0.2 core plus v0.2.2 privacy handling from a deleted prior repository. v0.3 adds the A-B-A benchmark and readout-frozen isolated probes. v0.4 adds locally persistent event observations and brain state in one SQLite transaction. Earlier PR numbers refer to the deleted repository, not this replacement.
- Issue #3: held-out generalization, retention, at least ten seeds and controlled growth ablations.
- Issue #4: opt-in, read-only internet senses with provenance and SSRF protections.
- Issue #5: grounded text-language interface and functional self-model with measured calibration.
- **Next decision:** prioritize end-to-end integration with independent evidence and no regression: a durable, bounded self-development supervisor (#8, #9), then secure internet sensing (#4) and grounded communication (#5). Continue #3 held-out evaluations as a release gate; do not equate model size with intelligence.

## Resuming in another chat

Give the assistant repository URL `https://github.com/promirmir/NeuroGenesis` and ask it to **read `AGENTS.md` and `docs/PROJECT_STATE.md`, inspect the latest `main` SHA, PRs/issues and Actions, execute tests, then continue the highest-priority verified milestone without regressions**. GitHub contains the state; no prior chat transcript is required for this workflow. Local untracked checkpoint files are **not** on GitHub and must be backed up privately by the operator.

## Non-regression gate

- All existing tests + CLI controls pass; saved-state backward compatibility tested.
- Output metrics are reported with seeds, benchmark/task specification and baseline; no cherry-picking.
- Changes with unverified behavior remain on PR branches; record failures in development log.
- Status document must be updated when capabilities, blockers or active milestone change.

## Privacy gate for every new chat

Public attribution: **Miron przy pomocy AI**. Block any full surname, private
contact details, credentials or secret paths in current tracked files and
commit *names*; e-mail in prior Git metadata may remain visible. CI runs
`python -m scripts.privacy_audit --git`. This is a scanner, not a guarantee
that old Git history or third-party caches have been erased. No forced history
rewrites without explicit verification.


## 2026-11-08 — held-out Markov baseline PR (pending validation)

Added dependency-free `neurogenesis/foundation_baselines.py` and `tests/test_foundation_baselines.py`: disjoint chronological 90/10 split, Laplace-smoothed unigram and first-order Markov next-byte cross-entropy (nats), no holdout fitting, no corpus upload or network. Run: `python -m unittest tests.test_foundation_baselines -v` and `python -m neurogenesis.foundation_baselines --input YOUR_OWN_CORPUS --confirm-corpus-rights`. This is an evaluation comparator, **not** a neural model or a demonstrated language gain. PR branch `research/markov-heldout-baseline`; no CI results or merge asserted. Next: validate Linux Python 3.11–3.13, actual foundation CPU, Windows EXE and privacy checks; compare identical independent holdout with FoundationBrain before reporting any performance claim.

## 2026-11-08 — Full chronological holdout evaluation candidate (unmerged)

Research branch `research/full-holdout-evaluation-20261108` replaces the first-window-only Foundation training metric with a deterministic token-weighted evaluation across all non-overlapping windows in the 10% chronological holdout. Window-boundary transitions are excluded; scored transition and window counts are reported. Real PyTorch regression tests cover weighting, short holdout and non-finite losses. Implementation commits: `9c7d5241ed3a7ec018e10f832e9ace7424ab9289`, `9896530d011e8ecebe84cb72d57c0d2ea6a2e444`. **Pending CI**: Python 3.11–3.13, dedicated Foundation CPU, Windows EXE; do not merge until green. No CUDA benchmark, independent language corpus or semantic understanding demonstrated. This evaluation still uses one adjacent split and is not prospective OOD evidence.
