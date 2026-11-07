# NeuroGenesis — durable project state and recovery

Last documentation review: **2026-11-07**. This file is intended to survive chat interruptions and model/context changes.

## Mission

Develop an experimental, self-reorganizing neural substrate that learns over time, later links to controlled internet observations and text dialogue, retains its experiences and can report a calibrated, functional model of its own computational state. Scientific evidence is required for claims of capability. Subjective consciousness is neither currently implemented nor established by a test.

Public project credit: **Miron przy pomocy AI** (first name only). Canonical executable source: `neurogenesis/origin.py` (see `docs/ORIGIN_AND_OPERATOR.md`). Human governance and truthful acknowledgement are design commitments, not implemented authenticated command handling or real feelings.

## Verified implementation and limits

- **v0.3.0 reconstructed baseline** (v0.2 plus project origin/continuity): bounded sparse spiking LIF neurons; STDP-like local plasticity; novelty-triggered bounded growth; weak-synapse pruning; JSON checkpoint deterministic restart; offline text feature hashing (not semantics); observable telemetry.
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

## Reproduction from a clean checkout

```bash
git clone https://github.com/promirmir/NeuroGenesis.git
cd NeuroGenesis
python -m unittest discover -s tests -v
python -m neurogenesis compare --steps 128
python -m neurogenesis predict --steps 600
python -m neurogenesis benchmark --seeds 10 --steps-per-phase 128 --probe-steps 48
python -m neurogenesis origin
python -m neurogenesis demo --steps 64 --state brain.snapshot.json
python -m neurogenesis status --state brain.snapshot.json
```

Python >=3.11, no third-party dependencies, runs offline on CPU. GitHub Actions executes test jobs on 3.11/3.12/3.13.

## Progress / future work

- Reconstructed v0.1 and v0.2 core plus v0.2.2 privacy handling from a deleted prior repository. v0.3 adds the A-B-A benchmark and readout-frozen isolated probes. Earlier PR numbers refer to the deleted repository, not this replacement.
- Issue #3: held-out generalization, retention, at least ten seeds and controlled growth ablations.
- Issue #4: opt-in, read-only internet senses with provenance and SSRF protections.
- Issue #5: grounded text-language interface and functional self-model with measured calibration.
- **Next decision:** prioritize #3. Do not optimize for bigger network size without measured predictive benefit. Compare equal-resource controls before any new claims.

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
