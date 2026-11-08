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
