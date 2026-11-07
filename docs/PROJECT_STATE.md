# NeuroGenesis — durable project state and recovery

Last documentation review: **2026-11-07**. This file is intended to survive chat interruptions and model/context changes.

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
