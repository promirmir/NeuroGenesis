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
