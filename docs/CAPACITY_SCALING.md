# NeuroGenesis: bounded capacity proposal (candidate v0.5.4)

Credit: **Miron przy pomocy AI**.

This is a candidate **non-destructive, bounded neural-capacity experiment**, not autonomous AGI scaling, GPU acceleration, Windows EXE build, autonomous cloud usage or autonomous source code changes. It is additive and preserves v0.4 neural and SQLite snapshot formats.

## Autonomous capacity logic

The `capacity_trial` procedure receives a `NextInputPredictor` and four distinct bounded sensory streams (`training`, `selection`, `audit`, `retained_skill`). The routine compares an incumbent trained on the same data with a clone whose **maximum** neuron and synapse capacities are increased within hard operator budgets. Growth on the cloned challenger still follows v0.4 novelty gating; the extra allowance does not force neurons to appear.

Acceptance requires all of the following: actual extra capacity used, size and CPU-work proxy within limits, improved selection MSE, improved **fresh independent audit MSE**, retained-skill MSE within tolerance of previous and incumbent states, and a maximum trial wall-clock deadline. Upon failure, the result is an **unchanged clone of the original**, not a damaged live model. Successful candidates are still **not persisted automatically**: the caller must independently validate, authorize and atomically commit them.

The candidate uses a frozen-probe implementation: model/readout trained state cloned; readout learning disabled, growth disabled, pruning age window protected and post-step synaptic weight updates reverted on the *probe clone*, while temporal neuron dynamics continue. Thus it compares predicted temporal sequences without permanent probe-side STDP. Original brain remains unmodified. This differs from earlier v0.4 `learn=False` semantics, which froze the readout but not STDP.

Scores are mean prequential next-input MSE; the first transition from a previous task is skipped. Compute proxy is sum of active neuron and synapse counts before each training step, **not measured power consumption**. Wall-clock is used as a fail-closed deadline; results may vary with system load. This method does not prove compute-matched comparison: candidate with more active units incurs more computational work, and can be rejected for that reason.

### Example

```python
from neurogenesis.capacity import capacity_trial, ResourceBudget, hardware_profile
model, report = capacity_trial(current_model, training=train, selection=choose,
                               audit=fresh_audit, retained_skill=old_skill,
                               budget=ResourceBudget(max_neurons=256, max_synapses=2048))
if report['accepted']:
    # Candidate model for separate transaction and operator-reviewed promotion.
    pass
print(hardware_profile())
```

`python -m neurogenesis.capacity` prints local CPU thread count and RAM if known. `--probe-cuda` optionally imports PyTorch solely for device discovery. Hardware discovery allocates **no GPU work**. Report fields explicitly mark GPU backend and distributed workers as unavailable, not implemented.

## Scientific and safety restrictions

- Never reuse independent audit/test streams across adaptation rounds. Any real production supervisor requires rotating private holdouts, data-source separation and operator-controlled memory retention.
- Tests using mocked scoring validate **decision gates**, not real independent learning gains. An accepted *mocked* test is not evidence of model superiority.
- Run the real 41 upstream tests and all new tests on 3.11/3.12/3.13 before merge; test on real Windows to produce a one-click EXE. No deployment without fixing privacy issue #6 (verified noreply Git author/committer).
- Distribution-shift, novel-task generalization, hardware energy/thermal management, CPU/GPU numerical parity, and user-authorized multi-computer orchestration remain research/development tasks.
- Keep resource ceilings user-owned: the brain may propose capacity but cannot raise its own limits, change permissions, purchase compute, or enlist third-party machines.

## First paired evaluation: negative result (2026-11-07)

Ten deterministic seeds, current **real v0.4** spiking `Brain` and online `NextInputPredictor`, using a restricted starting configuration with 24 neurons/16 synapses and allowance for one or more new neurons. All 10 candidate networks grew one neuron under their novel inputs and consumed **7.03%** more neural work proxy per training step than the fixed-capacity comparator. No candidate exceeded the preregistered selection gain threshold of 0.0001 MSE; **0/10 proposals promoted**. Positive selection gain did occur on some seeds but was too small. This is the correct decision under the predeclared limits; nothing about the failure implies that structural growth is universally harmful.

Reproduce with `capacity_trial()` and deterministic streams in `tests/test_capacity.py`; a machine-readable seed-by-seed report is provided separately as `NeuroGenesis_v054_10seed_results.json` in the originating conversation. The test sequences are synthetic shifted versions of one pattern family, so this is **not a scientifically independent proof of generalization**. Numeric resource work is only a computational proxy, not measured watts.

The capacity candidate also guards the **maximum cumulative training work units** and checks a wall-clock deadline before every training step, returning the original state on failure. This avoids allowing unrestricted expensive experiments even when the eventual candidate would be rejected.
