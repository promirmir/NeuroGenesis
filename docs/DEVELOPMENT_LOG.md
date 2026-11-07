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
