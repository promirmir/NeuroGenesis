# Development log — append-only milestone history

## 2026-11-07 — Research baseline v0.1 (PR #1)

Sparse CPU spiking simulator, local synaptic plasticity, bounded growth/pruning, deterministic JSON save/load, toy growth comparison, tests and CI. Results show structural growth only, not intelligence.

## 2026-11-07 — Online prediction v0.2 (PR #2)

Causal next-input predictor trained by online prediction error; fixed-structure comparison; prediction checkpoint; tests. Both networks improve on a repeating sequence without demonstrated growth advantage.

## 2026-11-07 — Provenance and recovery v0.2.1

Added canonical historical origin and AI collaboration record, acknowledgement policy, regression guards, compatibility handling for old snapshots, `origin` CLI, `AGENTS.md`, durable `PROJECT_STATE.md`, and operator guidance. These are infrastructure for continuity and governance, **not** newly acquired consciousness or semantics. Verify unit tests and three-Python CI prior to merging.

## 2026-11-07 — Clean rebuild after privacy incident

Clean-room tree reconstructed from verified local v0.2.1 sources, keeping tests and public API. Official public credit is **Miron przy pomocy AI**, including snapshots and CLI; compatibility adapter strips prior longer names during legacy checkpoint import. Added repository privacy-audit gates and a noreply-only initial publishing script. No subjective-awareness claim. The old public repository was deleted by its owner. GitHub commit history must be replaced in the new repository by a privacy-safe root commit; this does not erase third-party copies or platform caches.

## 2026-11-07 — v0.3 reconstructed pilot benchmark

Added readout-frozen isolated probes and an A-B-A continual-learning benchmark
across 10 paired seeds. The growth-enabled network did not outperform fixed
structure (A-after-B MSE 0.14877 vs 0.14565 on the synthetic pilot).
Added test cases for deterministic replay, probe isolation, input validation,
family-name privacy checks and recovery documentation. The original GitHub repo
was deleted and rebuilt; old references must not be mistaken for this repo's
PR history. No consciousness or generalization claim.

## 2026-11-07 — v0.4 private episodic memory and restart continuity

Added SQLite experience store, atomic persistence of each sensory event and
updated spiking neural state, optional raw text retention, fingerprint/hashed
feature recall, explicit deletion with non-unlearning warning, and CLI
commands `remember`, `recall`, `memory-status`, `forget-event`. Added 7
regression tests and .gitignore rules for private databases. All prior
simulator and prediction interfaces remain unchanged. No semantic or conscious
memory is claimed.


## 2026-11-07 — v0.5.4 GitHub merge and Windows EXE (PR #10)

Merged the additive experimental neural homeostasis, bounded repair and memory-guided rewiring, non-neural control, task-level evaluation, bounded self-development/capacity search, native Polish Tkinter application, and Windows single-EXE build workflow. Main landing commit `ddf6d3aa9c878c6f2ec221289521cf00349f8cba`.

Verified on actual GitHub Actions: `research-core-ci` passed on Python 3.11, 3.12, 3.13; Windows ran 125 tests, compiled the PyInstaller `--onefile --windowed` EXE, smoke-tested its SQLite self-test, generated SHA-256 and uploaded the `NeuroGenesis-Windows-x64` artifact. The first Windows CI attempt exposed SQLite handles left open in three tests, fixed by explicit connection cleanup. A subsequent EXE CI issue was caused by PowerShell not waiting for a windowed process; fixed via `Start-Process -Wait -PassThru`. Main rebuilds passed (Linux run `42414996746`; Windows run `42414996678`).

User-approved Git email publication unblocked Git work; author display names were independently checked for safe aliases without surnames, and code privacy scans remained enabled. No history rewrite was used. Earlier claims of privacy-related source commit blocking are superseded by current policy in `docs/PRIVACY_AND_AUTH.md`.

**Research limitations:** The native app is not an intelligent natural-language chatbot. Internet sensing remains OFF, no CUDA/distributed executor, and no continuous autonomous self-development supervisor. Most learning/repair evidence remains limited to synthetic experiments; some independent controls are stronger. Do not claim human-brain emulation, general intelligence, self-awareness or production reliability.


## 2026-11-07 — v0.5.5 opt-in supervisor integration (PR candidate)

Added a controlled periodic trial loop based on fresh private SQLite sensory observations. It uses the existing bounded self-development algorithm on a clone, distinguishes training/selection/audit/retention, persists a successful candidate readout and the *same neural brain* in one transaction, and records decisions with a rollback checkpoint. Default UI mode is OFF. No external actions, self-written code or unbounded execution. Windows and Linux CI must still validate this candidate before it can be called a released milestone.


## 2026-11-07 — v0.5.5 merged and missing-state fail-closed hardening

The first opt-in local self-development supervisor was merged to main in PR #12 (bbd9c00c557a2e87621cf81c598195109f8e7716). Original and newly added tests passed on Linux Python 3.11–3.13 and Windows, including frozen EXE smoke. A subsequent narrowly scoped hardening change prevents silent reinitialization of a missing brain snapshot in a database retaining experiences, and adds corruption regressions. No self-modifying source code or unconsented Internet access is enabled.


## 2026-11-07 — Persistent GitHub Releases for Windows binary (publication automation)

Added a dedicated `workflow_run` GitHub Actions release pipeline. Only successful Windows binary builds triggered by a push to the **latest main** can publish; the publishing job has isolated `contents:write` and `actions:read` permissions. It downloads the verified build artifact, checks `sha256sum --check`, confirms a Windows PE x64 executable, then creates a unique commit-bound release tag with EXE and SHA-256 assets. No manual archive browsing is required: latest EXE is linked prominently from README, the Polish setup guide and the project state document. Release publishing is still pending until verified on GitHub after merge; do not confuse a workflow definition with an actual release.


## 2026-11-07 — v0.5.6 explicit teachable dialogue (candidate)

Target user-facing gap: previous conversation always returned an acknowledgement and could not answer even directly taught questions. Added a clearly labeled, manually supervised local question/answer association table in the same SQLite brain database; teaching and four real neural steps share one transaction. GUI has Teach/Delete controls, corrects existing pairs, answers only exact normalized taught questions, otherwise acknowledges unknowns. No internet, unapproved auto-learning or generative language claim; no old raw observations converted into saved text. New tests cover restart, overwrite, privacy, rollback, corrupted data, long-message compatibility and predictor coupling. Full GitHub Actions CI/Windows EXE validation and merge are required before distribution.


## 2026-11-07 — Architectural pivot from toy SNN to learnable GPU-ready foundation (issue #18)

User correctly identified the mismatch between the small 24-neuron/8-channel prototype and the ambitious research goal. Abandoned PR #17 as a proposed cognitive milestone (closed unmerged; comparison branch retained). Started an entirely separate optional PyTorch foundation: ordered byte representation, fused trainable fast recurrent network, slower chunk memory, next-byte/latent prediction, local permissioned data training and atomic numerical checkpoints; dedicated CPU PyTorch CI and actual learning tests required. Old v0.5.6 EXE, small SNN, private SQLite and release process must remain stable. No claim of semantic competence or biological brain equivalence until independently demonstrated.


## 2026-11-07 — v0.6.0 candidate: opt-in live HTTPS sense + durable mission

Captured the complete long-term mission in docs/VISION.md: powerful scalable learned neural foundation with GPU, long-term memory, self-development, grounded live internet and an observable Windows GUI, without false claims of a biological brain or world-first achievement. Added strictly operator-enabled HTTPS read-only perception with public DNS/IP pinning, TLS hostname verification, no redirects, bounded MIME/body, inert HTML extraction and client-side query/credential blocking. Local input can refresh one approved address at five-minute intervals; source URL, SHA-256, UTC and existing brain sensory changes persist in one SQLite transaction. Deduplicated identical pages avoid repeated neural learning. Network is OFF on program start. Extended real GUI, tests with fake DNS/network and real SQLite, plus frozen EXE synthetic web smoke. The downloaded text currently trains the old limited LIF sensory system; the Foundation Brain remains independent and must be trained/benchmarked before real language cognition is claimed. PR not merged until CI passes.


## 2026-11-08 — held-out Markov baseline PR (pending validation)

Added dependency-free `neurogenesis/foundation_baselines.py` and `tests/test_foundation_baselines.py`: disjoint chronological 90/10 split, Laplace-smoothed unigram and first-order Markov next-byte cross-entropy (nats), no holdout fitting, no corpus upload or network. Run: `python -m unittest tests.test_foundation_baselines -v` and `python -m neurogenesis.foundation_baselines --input YOUR_OWN_CORPUS --confirm-corpus-rights`. This is an evaluation comparator, **not** a neural model or a demonstrated language gain. PR branch `research/markov-heldout-baseline`; no CI results or merge asserted. Next: validate Linux Python 3.11–3.13, actual foundation CPU, Windows EXE and privacy checks; compare identical independent holdout with FoundationBrain before reporting any performance claim.

## 2026-11-08 — PR #21 CI failure diagnosis and fixture correction

Initial PR head `f11a78bf6e57b227fbcce29f2c784632e719c437` failed Linux research-core CI run `42423006988` (Python 3.11/3.12/3.13) and Windows regression run `42423006975`: `test_holdout_never_updates_training_counts` expected 90 training bytes but built a 180-byte prefix (`bytes([0, 1] * 90)`), producing a 171-byte chronological training split. Fixed the test fixture to `bytes([0, 1] * 45)` in commit `805d52cfbe7f6c74ab9fd35f0aa33438935b5d3e`. This is a test fixture correction, not evidence of model improvement. Fresh CI, dedicated real PyTorch CPU and Windows frozen EXE checks remain required before merge. No GPU benchmark has been performed.

## 2026-11-08 — Full chronological holdout evaluation candidate (unmerged)

Research branch `research/full-holdout-evaluation-20261108` replaces the first-window-only Foundation training metric with a deterministic token-weighted evaluation across all non-overlapping windows in the 10% chronological holdout. Window-boundary transitions are excluded; scored transition and window counts are reported. Real PyTorch regression tests cover weighting, short holdout and non-finite losses. Implementation commits: `9c7d5241ed3a7ec018e10f832e9ace7424ab9289`, `9896530d011e8ecebe84cb72d57c0d2ea6a2e444`. **Pending CI**: Python 3.11–3.13, dedicated Foundation CPU, Windows EXE; do not merge until green. No CUDA benchmark, independent language corpus or semantic understanding demonstrated. This evaluation still uses one adjacent split and is not prospective OOD evidence.

## 2026-11-08 — Candidate PR #24 (unverified)

Added opt-in specialist Wikipedia source study controller, tests, native Tk tab and GUI-thread SQLite persistence. Head before documentation: `44e579c71335f6ae02d568aaba99244bb81280dd`. No model-weight training or broad web crawling. Do not merge until Python 3.11–3.13, privacy and Windows EXE checks are green.

## 2026-11-08 — Autonomous public-web specialist discovery candidate, PR #24

Expanded specialist session beyond Wikipedia seeds: validate and extract up to 256 HTTPS links per HTML page, follow topical links across up to 50 public domains with robots.txt and crawl-delay, sequential rate/crawl budgets, operator-adjustable 1–500 page attempts, UI source discovery/progress and existing local SQLite provenance. A separate explicit 512 KiB crawl page cap leaves the manual 128 KiB default unchanged. Offline tests cover robot exclusions/redirects, SSRF URL rejection, cross-domain behavior and bounded HTML extraction. Source milestone `8c845dd60d68691bbc92393bb4e0863e2db3f6ea`; documentation commit `f3cb741ff2af3bc096f6cb4893dce858386ac098`. This is not whole-Internet indexing, forum completeness, semantic expertise or Foundation Brain weight training. At documentation time final Python/Windows tests are not yet verified. Keep PR draft until all gates green.

## 2026-11-08 — PR #24 merged and release verified

Feature head `c90126532de97189d3717b4adabb25d71a0b55fe` passed Python 3.11–3.13, privacy and Windows standalone EXE smoke before merge. PR #24 squash-merged into main `578222800c5adc73c0a756352b5bef405535252a`. Main Python run `42463459779`, Windows EXE run `42463459963` and release publish run `42463541158` completed successfully. Immutable release `v0.6.0-main.57822280` contains `NeuroGenesis.exe` and checksum; EXE digest SHA-256 `20708872a4c2b35484da100a88794aaef321e329d469524eb63162b4638b4731`. Tests validate mocked public-web traversal and EXE packaging, NOT exhaustive web coverage, real-site success, or semantic expertise.

## 2026-11-08 — Original vision versus deliverables audit (documentation)

Measured development status against `docs/VISION.md` using repository `main` `db0b2210bb97c422d83d27f963725d3d6941c067` and the public release `v0.6.0-main.db0b2210`. Wrote `docs/DELIVERY_AUDIT.md` with a code-grounded feature matrix, critical missing web→knowledge→Foundation→conversation integration, missing UI quality/observability, no verified GPU performance/distributed execution, and staged measurable acceptance for v1. Audit did not run an independent user-facing Windows GUI session or real public web crawl; GitHub CI evidence is not substituted for those tests. No Python implementation change in this documentation PR.

## 2026-11-08 — PR #23 current-main reconciliation candidate

- Reconciled old PR #23 with current main `542ba8272ceb4c0c13871b9f9fd954c23d4c4cdb` while retaining prior PR changes. Added a missing Windows-EXE workflow PR trigger for `.github/workflows/foundation-cpu.yml` so this CI-only change can receive its previously absent Windows regression/packaging gate. The dedicated real-PyTorch job now includes held-out baseline tests on relevant file changes.
- No runtime code, SQLite schema, neural training or release change. Pending fresh CI and explicit merge decision; do not count old green checks as validating the updated head.

## 2026-11-08 — PR #23 completed; source evidence integration PR #27 candidate

- CI PR #23 squash-merged to main `66f3d61fa1696aaeeb3c33c0d035100a9aaacba1` after all five checks: Python 3.11/3.12/3.13, real PyTorch CPU foundation and Windows standalone EXE (privacy checks included).
- Added dependency-free `neurogenesis/knowledge.py` and `tests/test_knowledge.py`: local bounded source passages + revisions + token index, exact quote and provenance retrieval, source deletion, unknown-question abstention; accepted web observations index in the same SQLite transaction as neural state, event and URL/SHA; no old brain/teaching data deletion.
- Extended existing Windows conversation and frozen EXE self-test to cite a source after reloading local SQLite; manual teachings always take precedence. No Foundation weight training, general text generation, online real-site benchmark or rights verification claimed. Controlled test fixture defines three answerable and two unsupported questions (coverage 0/3 before and 3/3 after synthetic source acquisition, *not* model accuracy).
- First Linux CI `42465142616`: 11/11 new knowledge tests green; one existing exact UI acknowledgment string test failed, so original text was restored in `d4fc8fe2a2b3ec2a5e0e06d70fbac96af4a417b3`. Fresh CI plus Windows EXE must verify final head. `docs/COMMAND_CENTER.md` is an additive Qt design specification, not a shipped GUI.

## 2026-11-08 — Optional functional PySide6 Command Center PR candidate

- Implemented `neurogenesis/command_service.py` to expose actual private SQLite/brain/knowledge state and run opt-in bounded `SpecialistStudy` in a background worker with revocable session-scoped consent and bounded progress queue. No network on startup, no optional dependency in legacy EXE.
- Implemented seven-panel `neurogenesis/command_center.py` PySide6 shell using live service metrics: Overview, genuine source-cited Chat, bounded public-HTTPS Research/Stop, real Brain.traces visualizer, honest inactive Training/CPU display, private Source browser and permission/diagnostics settings. This is real source code, not a screenshot or guaranteed runnable Windows package before CI.
- Added optional `[command-center]` dependency, dedicated actual PySide6 Windows/Linux offscreen CI, headless service and GUI smoke tests, source passage API and `docs/COMMAND_CENTER.md` release/licensing boundaries. Old Tk onefile and database remain unchanged. Await required CI/packaging/privacy validation, do not merge on failures.

## 2026-11-08 — PR #28 merged and Qt Windows executable technical packaging gate

- PR #28 squash-merged to main `2bd5af5a1db70dee8566f848a41d5024e8fa8bba`; all required Python 3.11–3.13, real PyTorch CPU, Windows frozen existing Tk app, actual PySide6 Qt offscreen on Windows/Linux and privacy CI green. This is verified Qt *source* operation, not released Qt EXE.
- Next candidate adds `command_center_launcher.py`, `--self-test` for the actual Qt GUI sourced answer across private SQLite reopen and `.github/workflows/qt-windows-frozen.yml` to build PyInstaller `--onedir` Qt application and test its executable; log SHA-256, uncompressed size and presence of replaceable dynamic Qt DLLs. No Qt artifact uploaded pending LGPL/third-party notice compliance and usability review. Original Tk release is not affected. Await new workflow CI.

## 2026-11-08 — Explicit rights-gated knowledge to Foundation model trainer (PR candidate)

- PR #29 merged on main `9388e19356c2d7f49ffdd1a72d0996d3d89986b0` after Python 3.11–3.13, real Qt Windows+Ubuntu, existing Tk EXE and actual frozen PyInstaller Qt EXE smoke succeeded. Qt directory 111.95 MiB, tested EXE SHA256 `2d563058b985f169ae04b39f8674f1f5d2a5fc85af0dbfc6d32b86c3501ac3b8`. No Qt public asset published pending license audit.
- Added additive `knowledge_rights_audit` and per-revision `operator-approved-local-training` marking, revocation and latest-only source eligibility. Separate CLI `knowledge_rights`; no automatic rights inference from public HTTPS.
- Implemented `knowledge_train`: selected approved private source excerpts actually update PyTorch Foundation Brain next-byte weights on bounded CPU or explicitly requested CUDA, with a whole-document held-out set, before/after CE and first-order Markov baseline, measured training steps/s, CUDA peak allocated bytes only if available. Checkpoint is separately saved as a private **candidate**, not installed in chat. No Internet call, external compute or hidden unlicensed corpus ingest.
- Added actual Qt source rights selection, explicit-per-session training opt-in, CPU/CUDA and steps controls, background worker metrics, cancellation, and honest validation display. Updated `.gitignore` for private .pt/.pth artifacts; new `docs/KNOWLEDGE_TRAIN.md` and real PyTorch tests. All **candidate** until GitHub Actions Python, Torch CPU, Windows Qt/EXE and privacy gates pass; do not claim neural inference or meaningful language competence.

## 2026-11-08 — validated and merged PR #30, closure of current implementation batch

- PR #30 squash merge `334b1afc842f662b422b8ca81404c3fd75874523` to `main`. Verified required checks: Python 3.11/3.12/3.13, privacy audit, actual PyTorch CPU, optional actual Qt offscreen on Windows/Ubuntu, frozen legacy Tk Windows EXE, and separate frozen Qt executable technical smoke. No Qt package published, no CUDA test on physical GPU.
- Actual foundation CPU test (final PR head `7eba795c4cfb77929f8d5efbe3c2a0a5ff94c327`, dedicated job `128691478314`) measured heldout next-byte CE `5.7385941651 → 5.5994535677` nats after 3 gradient steps, aligned Markov baseline `1.7341137780` nats (better than neural model). Real candidate weights and checkpoint, not semantic chat competence. Standard CPU suite 223 tests with 1 optional skip on the test job; real CPU-specific 9 checks passed.
- The resulting user-facing Tk EXE preserves original dialogue and now cites local saved source evidence. Qt source app supports opt-in rights-governed training but remains optional pending licensing and package distribution. Do not regress the existing private SQLite DB or present retrieval as learning weights. See [KNOWLEDGE_TRAIN.md](KNOWLEDGE_TRAIN.md).

## 2026-11-08 — next isolated real-weight inference PR candidate

- Verified fresh main `0afcb2b37ee908c4810b6c545e8833ebef9fd787`, no open PR. Implementation branch `feat/foundation-inference-lab-20261108`: new `foundation_infer.py` uses the actual trained FoundationBrain checkpoint to run bounded autoregressive greedy byte predictions, trust validation, untrained-checkpoint rejection, cancellation and measured inference time. Does not write private SQLite, call network or inject uncited neural text into user chat.
- Qt Training page now separates an explicitly opted-in experimental inference lab from sourced conversation. It can use an operator-selected local checkpoint and display raw hex plus replacement-decoded text with explicit NO SOURCES / NO VERIFIED FACTS designation. New mandatory real CPU test and service/Qt regressions added, with expanded foundation CPU workflow trigger.
- See `docs/FOUNDATION_INFERENCE.md`. This milestone is **candidate until all CI and frozen Windows checks succeed**. No independent text understanding, physical CUDA, v1 readiness or redistributable Qt package claimed.

## 2026-11-08 — PR #32 merged, independent old/new model retention audit candidate

- PR #32 merged to main `ec5bc9fcfdbc2fa7c940e33fc8b090a48ed610b7`, with Python 3.11–3.13, real PyTorch CPU, Qt Windows/Ubuntu, both Windows frozen EXE checks and privacy green. Real checkpoint inference lab is isolated and does not replace source-cited chat or deploy weights.
- New branch `feat/foundation-candidate-retention-audit-20261108` adds a side-effect-free numerical candidate acceptance check: load separate trained incumbent/candidate checkpoints, score **both** against the same old-task and same new-task held-out files; require bounded old-skill regression and actual new-task gain before declaring a narrow numerical pass. Result **never** promotes a checkpoint. Explicit local rights/trust mandatory, same architecture, immutable audit text and SHA-256, no network or SQLite.
- Dedicated real PyTorch CPU tests cover numeric positive/fail thresholds and full checkpoint evaluations against fictional documents; CI is not yet complete. See `docs/RETENTION_GATE.md`. Independent naturally sourced QA/semantic competence, prospective audit provenance, actual GPU performance and Qt legal distribution still open.

## 2026-11-08 — controlled continued Foundation weight learning (candidate)

- PR #33 merged to main `fd4ab6a723baad237d583d62991dbfdcd84b3f74`, with dedicated real CPU Torch, Python 3.11–3.13, privacy and Windows EXE green. Fictional paired benchmark: old CE 5.71674→5.69102, new CE 5.74617→5.74156; new ~0.08% gain below 1% gate, so candidate numeric pass is **false**. No automatic promotion.
- Implemented optional `resume_from` and explicit `trust_resume` for `knowledge_train`: read-only numerical trained checkpoint load; reject missing, mismatched, untrained, untrusted, existing output and source/SQLite collisions; continue weights with real Torch updates, separate atomic candidate, SHA256 of prior checkpoint and cumulative step count. AdamW optimizer intentionally **reinitialized**, not a resumed optimizer state. Approved corpus rights remain mandatory; old source not changed.
- Added local Qt continuation checkbox + control flow to service worker. Real CPU regression covers two-stage continued learning and preservation of original checkpoint including asynchronous service; await all CI before merge/release. No claim of real contextual language competence.

## 2026-11-08 — PRs #32–#34 merged, genuine checkpoint inference and continued learning

- PR #32 `ec5bc9fcfdbc2fa7c940e33fc8b090a48ed610b7`: operator-trusted real PyTorch Foundation checkpoint inference, bounded greedy next-byte sampling, raw hex/UTF-8 and actual throughput, cancellation, optional isolated Qt lab. Never auto-promoted into source-cited chat. All PR Python/real Torch/Qt/Windows/EXE/privacy tests green.
- PR #33 `fd4ab6a723baad237d583d62991dbfdcd84b3f74`: old/new-domain paired candidate evaluation for genuine checkpoints with independent operator-supplied UTF-8 test documents, explicit trust/rights, no automatic promotion. Real CPU fictional benchmark old CE 5.7167409→5.6910159, new CE 5.7461666→5.7415593; 1% new-task improvement threshold **not** met. Python 3.11–3.13, real Torch, privacy and old Windows EXE green.
- PR #34 `6a45379c2310bc0622b932e21406feddbdbdcd4d`: opt-in checkpoint weight restoration and further actual Torch updates; same model config; per-source corpus rights; prior checkpoint SHA preservation; new-file only, fail-closed on existing filename; separate Qt checkbox and worker. AdamW optimizer starts fresh, not exact optimizer-state restoration. Fictional real CPU test 2-step previous +2-step resumed, total4; holdout CE 5.6478154→5.5607319 nats, still not better than Markov. Python 3.11–3.13, real PyTorch CPU, Qt Windows/Ubuntu, old Tk EXE, separate Qt frozen EXE and privacy checks green before merge. Main release is independently validated only after successful publishing.
- This completes the **engineering link** from local approved source snippets to measured trained weights, experimental inference and bounded continued learning. It does NOT complete meaningful neural reasoning, source credibility/contradiction handling, GPU benchmark or a user-ready professional Qt installer. See status and research gates above.

## 2026-11-08 — local two-source evidence comparison with cautious contradiction signals (candidate)

- Verified baseline `main=200a78cbe7e60777a9fc6a368268c6a055b74c4d` after docs PR #35; source evidence retrieval remains lexical.
- Added up to two **verbatim** passages from different source hostnames among the newest URL revisions, retaining original best-ranked passage as first. Existing `source` response property kept; additive `sources` list and `evidence_review` contain provenance and conservative discrepancy flags. Number differences and explicit negation mismatches only prompt human review; no conclusive contradiction, fact checking, site independence or accuracy claims.
- Extended source-cited default Tk + Qt responses to carry both citations; explicit user-taught answers still override and empty queries abstain. Added offline SQLite/restart, two-host, same-host, stale revision, numeric/negation and unsupported QA tests. No network, third-party data or actual Torch training. Await CI and merge before claiming this shipped in EXE.

## 2026-11-08 — candidate: session-only contextual follow-up anchored to stored evidence

- PR #36 merged to main `0bcfb6a158c57465b0b39dda26e4ed3ca20e22bd` after green Python 3.11–3.13, actual CPU Torch, privacy, Qt Windows/Ubuntu and Windows frozen Tk EXE. Different-host verbatim excerpts and numeric/negation review flags do not claim verified contradictions.
- Added `dialogue_context.py` conservative explicit Polish follow-up detection; enrich retrieval with prior sourced topic, require novel substantive term in passage AND previous exact URL/latest revision. Service holds only volatile last grounded question/URL; process_message persists original user sensory text hash as before, not expanded prompt/raw personal dialogue. Manual teaching wins; unsupported queries abstain and reset topic; Qt provides a clear-context button without erasing stored brain/knowledge.
- New offline source/Qt integration tests for successful constrained followup, same-domain scope, revision replacement, cross-site refusal, private SQLite and teacher priority. Tests/CI pending; no claim of neural semantic understanding or automatic memory across restarts.

## 2026-11-08 — offline evidence-citation QA evaluator (PR candidate)

- PR #37 merged into main `c94dce00761d938e12215b19c20dbfd9efe426a9` after real CPU PyTorch, Python 3.11–3.13, Qt Windows/Ubuntu, Windows frozen Tk and Qt technical EXE, privacy green.
- Added `qa_eval.py`, a deliberately read-only, consent-gated evaluator for a local operator-supplied **holdout** JSONL of source-answerable and unsupported questions. It measures literal quote and exact cited URL success, source precision, false citations, abstention and query latency percentiles. A new `quoted_evidence` structured field links each verbatim quote back to the exact URL rather than assuming a whole answer string represents one source. No manual/brain memory mutation, no downloads or tool-driven model training.
- Offline tests using fictional NeuroGenesis source documents intentionally include one unsupported query sharing lexical overlap, to reveal any over-answering; CI outcome pending. This does not measure semantic neural model reasoning or verified factual correctness. Full limitations in `docs/QA_EVALUATION.md`.

## 2026-11-08 — PR #36–#38: citations, constrained context, read-only QA quality metrics

- PR #36 merged `0bcfb6a158c57465b0b39dda26e4ed3ca20e22bd`: up to two newest-version quoted evidence passages from distinct hostnames with exact URL/revision and **potential** number/negation discrepancies requiring human inspection. No verified fact/independent publisher claim. Real SQLite/tests, Python 3.11–3.13, actual Torch CPU, Qt Windows/Linux, privacy and Windows frozen Tk EXE green.
- PR #37 merged `c94dce00761d938e12215b19c20dbfd9efe426a9`: bounded one-session Qt followup context scoped to previous cited URL/latest revision and requiring a new focus token to occur in the quote. No hidden raw transcript persistence or cross-site answer inheritance. Clear-context preserves SQLite; manual taught answers retain precedence. Same CI gates green including technical frozen Qt EXE.
- PR #38 merged `4a81cc76a3191ee4031e8bfde9430626a50914ad`: added independent local read-only `qa_eval` JSONL evaluator and URL-bound `quoted_evidence` metadata. Synthetic 6-question audit reports 3/3 supported exact quotes, 2/3 unsupported abstentions, **one false citation** (33.3% false-citation rate on this tiny negative set), total 83.3% strict fixture accuracy, actual p95 lexical SQLite-only query ~0.336ms on Linux CI. All Python/real Torch/Qt/Windows Tk/privacy PR checks green. A matched real-world/independent natural QA evaluation and trained semantic response quality remain unproven.
- All prior checkpoint inference, rights-approved training, optimizer-reset continued learning and retention tests remain intact, but they are byte-prediction research modules, not the source of normal chat answers. Latest Windows publication/post-merge build must be checked separately; Qt legal redistribution remains blocked pending licensing/packaging review.

## 2026-11-08 — verified Windows Tk release for PR #36–#38

- GitHub release `v0.6.0-main.4a81cc76` successfully published for exact main `4a81cc76a3191ee4031e8bfde9430626a50914ad` after Windows standalone EXE smoke and SHA-bound release workflow. 13,044,179-byte `NeuroGenesis.exe` digest `ad30b2f245a77055feca9557f426b77d5c6298d8e0a0e3a31cf727270e5a293d`. This is the Tk executable; Qt source/technical smoke is separate and not redistributed yet.

## 2026-11-08 — strict polar claim coverage to reduce unsupported citations (candidate)

- Starting main `87127d13921a9c4840163cc67e1b3d52c6b5310a`. A pre-existing fictional QA fixture reported a wrong source citation for an unsupported yes/no assertion with lexical subject overlap; PR #38's QA evaluator is read-only and remains unchanged.
- Implemented conservative claim coverage for direct `Czy...` and explicit contextual `A czy...` questions. Only quote if **every** substantive claim token in the question appears in the same saved newest-revision passage and explicit negation is consistent. Otherwise abstain; no inference from mere subject words. Intentionally conservative, limited to literal words and not factual validation.
- Add new fictional polar-question tests (positive, unsupported qualifier, polarity mismatch, negative source, old teaching priority), adapt cross-host negation-review test to a nonpolar query, and do not call improved scores on the *already seen* QA fixture an independent quality gain. Await required CI before merge.

## 2026-11-08 — prospective literal-source QA acceptance gate candidate

- Live main at start `da9a6c736f55c13b048101a4a07c2f5defff64a1`, with no open PR and full recent main CI green. Existing polar-question coverage and observed six-question false citation remain a seen in-sample development test; do not tune for fixture perfection and claim generalization.
- Implemented `qa_acceptance.py` using development/prospective JSONL disjoint normalized questions, actual read-only SQLite `qa_eval`, Wilson 95% intervals for supported quote recall and unsupported false citation, trivial abstain-all baseline, class minimums and explicit no-release/no-neural chat status. Default threshold penalizes false citations with confidence bound; no private text in report.
- Added separate fictional real SQLite quality gate tests including unsupported propositions that share subject tokens, no database writes, normalized question overlap denial, sample sufficiency/uncertainty checks, and a dedicated no-network GitHub Actions workflow. See `docs/QA_ACCEPTANCE.md`. Requires CI before merge; not an independent real-world claim.

## 2026-11-08 — matched BM25 source-retrieval baseline candidate

- PR #41 merged `7dd3094ac791b241b2b84d50dccb0fa3032bc8b6`; full Python 3.11–3.13, dedicated offline real SQLite QA CI, privacy and Windows frozen EXE green. Synthetic public fixture 40 supported + 100 unsupported: observed quote recall 1.0, observed false citation 0, Wilson upper95 0.03699; **not** an independent empirical QA claim.
- New candidate `neurogenesis.qa_baselines` implements classical BM25 k1=1.2, b=.75 over latest local SQLite revision only and compares to *unchanged* production `answer_question` on precisely the same rights-cleared/heldout local QA JSONL. Reports literal citation recall, unsupported false citations, strict score and median time for both; no switch to BM25, no model training, no SQLite writes, no raw text output. Fictional tests include unsupported shared-topic premise and historical URL version supersession. See docs/BM25_BASELINE.md; CI pending.

## 2026-11-08 — verified source QA uncertainty gate and BM25 reference (#41–#42)

- PR #41 merged `7dd3094ac791b241b2b84d50dccb0fa3032bc8b6` after Python 3.11–3.13, dedicated offline QA, privacy and frozen Windows Tk EXE passed. Added operator-approved read-only development/independent-prospective JSONL split, exact normalized question contamination check, confidence-bound Wilson supported recall/unsupported false citation, abstain-all baseline and strict *numeric only* acceptance. Public fictional CI 40/100 tested: 100% quote recall, 0 observed false citations, Wilson upper false 0.03699. No generalization conclusion possible.
- PR #42 merged `a29ba37689c0bfe21cba028d1c819428fe40da09` after equivalent Python 3.11–3.13/dedicated QA/privacy/Windows frozen EXE green. Added genuine repeated-term BM25 control over latest source passages, paired comparison on identical heldout questions and no mutation/automatic deployment. Fictional CI example produced equal 80% strict score for incumbent/BM25, both with 1/3 unsupported false citation. First CI caught a Python token-variable defect and formatting error; fixed and all final feature-head checks passed.
- No trained semantic grounding or licensed independent human QA performed. No change to legacy Tk/Qt conversation engine or memory, no physical CUDA measurement. The verified EXE at handoff remained `v0.6.0-main.7dd3094a`; newest #42 main artifact publication requires separate check.

## 2026-11-08 — version 0.7.0 research stabilization candidate: transactional private-memory recovery

- Started from verified `main` `bf77bb08819dfe626587e170b35e159df14bf931` with no open PR; Windows standalone, Python and publish CI were green. Qt public licensing remains unresolved and semantic natural QA not independently validated.
- Added `neurogenesis.recovery` for explicit offline, consistent SQLite backups under WAL, read-only `quick_check`, full brain snapshot and schema validation, SHA-256, no-overwrite atomic filesystem publication, verify and confirmed restore to **new file only**. Never delete or overwrite existing SQLite, never upload source text. Full private copied state includes brain, manual answers, documents, versions, rights audit, with no external `.pt` checkpoints bundled.
- Added background Backup/Verify panels to Tk Windows EXE and optional Qt, keeping UI responsive and permission OFF; Windows EXE self-test also runs genuine backup/verify/restore. Tests cover SQLite backup/restore/restart, WAL, corruption refusal, symlinks and no-overwrite.
- Raised version metadata to 0.7.0 as a **research toolkit stabilization** milestone, cleaned README to remove old contradictory candidate history; does not establish AGI, natural semantic chat, physical CUDA hardware gain or legally releasable Qt EXE. Entire branch **pending CI and publication** at time of writing. [Runbook](MEMORY_RECOVERY.md).
