# NeuroGenesis: measured biological-core candidate v0.5

**Public credit: Miron przy pomocy AI.** This is research software, not a
human brain emulator, biological organism, conscious entity or demonstrated
human-level intelligence.

## Purpose

The neural substrate must be the actual source of adaptation. Language adapters
and internet sensors are secondary interfaces, and their capabilities cannot be
attributed to the substrate without causal ablation experiments.

Biology-inspired mechanisms must improve **independent predictive accuracy,
retention, adaptation, fault tolerance or compute efficiency**, not simply
increase the number of neurons.

## Existing baseline

v0.4 has a bounded LIF spiking network with local trace-based plasticity,
novelty-based structural growth, an online next-input predictor and SQLite
experience persistence. In the recorded 10-seed A-B-A benchmark, growth ON
had *worse* retention than growth OFF; there is no proven growth advantage.

## New candidate modules (NOT merged, not automatically enabled)

- `neurogenesis/homeostasis.py`: an activity-rate EWMA controller with bounded
  postsynaptic synapse scaling, an input-evidence gate, deterministic state,
  and explicit attachment to an existing brain without resetting it.
- `neurogenesis/repair.py`: deterministic synaptic lesion **on a clone**,
  proposal of bounded compensatory paths to disconnected hidden neurons,
  and acceptance gated by a caller-supplied validation error. No exact
  reconstruction of destroyed synapses or memories is claimed.
- `tests/test_homeostasis_repair.py`: isolated contract tests, including
  invalid parameters, bounds, silent input, growth, resume, repeatability,
  clone-only injury and rejection of ineffective candidates.

The original `Brain.step()` and v0.4 persisted schema are deliberately unchanged.
The controller can be snapshotted separately. The candidate does **not**
automatically restore/controller-synchronize from SQLite; integrating that
atomically with the state is a separate versioned change and mandatory before
continuous autonomous deployment.

### Mathematical assumptions

At each observed time step, for neuron i:

```
r_i[t] = beta * r_i[t-1] + (1-beta) * spike_i[t]
```

After `adapt_every` valid steps with a sufficient number of nonzero input
samples, each incoming synapse to a hidden neuron is adjusted by:

```
f_i = clip(exp(eta * (target_rate - r_i)), 1-delta, 1+delta)
w_ji <- clip(w_ji * f_i, 0, weight_limit)
```

within a dead-zone around the target rate. `delta` limits the per-interval
multiplicative change. **This is one engineering approximation of homeostatic
scaling, not a physiological calibration.** Input channels are not regulated;
zero-input periods never amplify synapses just to force non-existent sensory
evidence. Repeated scaling may still accumulate; test long-term stability.

A structural repair trial creates a copy of the damaged substrate and adds
bounded candidate paths into disconnected hidden neurons. The caller supplies
an explicit error function on a validation stream. A proposal is accepted
only if `error_before - error_candidate > min_improvement` and never changes
the original brain object. Selection on validation is not a final test score.

## Required integration and research gates

1. Apply the candidate patch to a clean v0.4 checkout. Run the 41 baseline
   tests, new contract tests and memory/CLI compatibility tests on Python
   3.11/3.12/3.13. No merging while the privacy metadata issue #6 is open.
2. Add **real Brain** integration tests: run `Brain.step` with paired stimuli,
   call regulator once after each step, test bitwise checkpoint resume,
   no-input behavior, structural growth and no out-of-budget synapses.
3. Record the controller's state atomically with the brain's SQLite state or
   via a validated, versioned transaction format; a restart must not reset
   learned neural history or replay an old regulator as if it were current.
4. Random **and targeted** synapse/neuronal lesions at 0/10/25/50%, with >=10
   predeclared paired seeds. Record MSE before injury, immediately after,
   and after candidate recovery; compare against damaged **without repair**
   under matched time/size constraints.
5. Separate validation and an unseen final holdout. Evaluate out-of-
   distribution sequences, memory retention, calibration, spikes, graph size,
   wall time and resource use. Perform no cherry-picking, report failures.
6. Compare pure LIF+STDP, LIF+homeostasis, LIF+repair, and both combined,
   keeping the legacy v0.4 outcome as a reproducible baseline.
7. If the neural substrate contributes no reproducible benefit over a static
   network or a simple Markov baseline, do not label it better intelligence.
8. Internet/web and dialogue must later be integrated through provenance-
   tagged sensory channels, with explicit consent and brain-disabled
   ablation, never arbitrary autonomous access or privileged source rewrites.

## Long-term research mechanisms (NOT yet implemented)

- Prediction-error-driven local synaptic learning and recurrent dynamics.
- Episodic indexing with selective offline replay and cortical consolidation.
- Slow intrinsic excitability plasticity and excitation-inhibition balance.
- Plasticity-of-plasticity, neuromodulatory curiosity/reward gating.
- Safe functional self-monitoring, validated structural compensation,
  continuous process lifecycle and bounded multi-computer coordination.

There is no agreed complete mathematical specification of a human brain;
matching a small subset of its equations does not establish a human-like
mind. Progress must be measured using behavioral and mechanistic controls.

## Neuroscience basis

- Wen & Turrigiano, *Annual Review of Neuroscience* (2024),
  https://doi.org/10.1146/annurev-neuro-092523-110001
- Turrigiano & Nelson, *Nature Reviews Neuroscience* (2004),
  https://doi.org/10.1038/nrn1327
- Ororbia, *Neurocomputing* (2023),
  https://doi.org/10.1016/j.neucom.2023.126292
- Dohare et al., *Nature* (2024),
  https://doi.org/10.1038/s41586-024-07711-7

## v0.5 actual-Brain integration checkpoint (2026-11-07)

We reconstructed the v0.4 source interfaces (Brain, Origin, Sensory, SQLite
ExperienceMemory) from the connected GitHub repository into an isolated local
workspace, because direct git clone was blocked by DNS. This is **not** a
full checkout and does not independently verify exact file checksums. The
unchanged original source is not bundled in this candidate patch.

- **26 new tests passed** locally under Python 3.13: 16 contract tests, 7
  actual-Brain integration and benchmark tests, 3 real-SQLite compatibility
  tests. All legacy tests and Python 3.11/3.12 CI remain unverified.
- The actual-Brain tests check growth, bounded weights, two independent
  regulator+brain snapshot trajectories, lesion cloning, trial rejection,
  malformed parameter handling and deterministic paired evaluation.
- SQLite tests check intact v0.4 memory on disk, no raw-text persistence by
  default, and fail-closed behavior for a corrupted neural state.

### Reproducible adverse finding

From the isolated source reconstruction, run:

```bash
python -m neurogenesis.lesion_benchmark
```

Protocol `intact_oracle_synapse_lesion_activity_v1`:
10 seeds, 160 training steps, 50% random synapse loss (8/16 removed),
72 validation steps, separate 96-step noisy holdout (noise amplitude 0.1),
proposed replacement weight 0.8. Mean held-out hidden spike disagreement
relative to the intact network:

| Condition | Mean error |
|---|---:|
| Damaged, no repair | 0.062500 |
| Naively add connections | **0.109375** (worse) |
| Propose and accept only if validation improves | **0.062500** (unchanged) |

**0/10 repair proposals were accepted**. The acceptance gate prevented a
regression but did not restore function. This result falsifies any claim
that naive rewiring is already functional self-repair. Additional 20-seed
local probing of stronger connections also found harmful outcomes.

**Crucial validity limitation:** reference activity is generated from an
intact oracle available only to the controlled experiment (or a previously
recorded functional fingerprint). It is not autonomously reconstructed after
loss. Hidden-spike agreement is only a proxy, not learned task accuracy or
restored memory; validation and holdout remain from a narrow synthetic family.
Neural plasticity is active during each isolated probe. Real self-repair
requires an independently grounded error signal, multiple candidate
policies and validation on true task retention.

### Integration gates still open

Apply additive patch in a verified clean GitHub checkout, run original 41
unit tests plus 26 new tests, compare under Python 3.11/3.12/3.13, and
inspect actual commit identity before any push. Don't merge while #6
remains unresolved. This patch intentionally does not autonomously change
source code or grant internet access.

## v0.5.1 memory-guided functional compensation (separate new module)

The naive repair proposal above was improved through **pre-injury recorded
neural activity**, rather than copying a surviving intact brain after damage.
The optional `fingerprint_repair.py` records numeric sensory streams and hidden
spike responses from a healthy copy, then searches for a small set of input-to-
fully-disconnected-hidden synapses which reduce mismatch against the stored
signature. It never alters the caller's brain or writes live SQLite, code or
configuration. No previously absent or erased fingerprint can be regenerated
from nothing. Fingerprints of personal inputs are sensitive derived data and
must be stored privately with consent if persisted in future versions.

Run the standalone reproducible test on a clean checkout containing this patch:

```bash
python -m neurogenesis.lesion_benchmark --fingerprint --seeds 10 --fraction 0.5
python -m unittest discover -s tests -v
```

Observed from the **local reconstruction of GitHub v0.4 source** (Python 3.13):

| Condition | Mean held-out hidden-spike mismatch | Number of seeds |
|---|---:|---:|
| 50% synapses removed (8/16), no repair | 0.0625000 | 10 |
| Fingerprint-guided compensation | **0.0421875** | 10 |

Paired improvement occurred in **10/10** seeds, with 2.6 connections added
on average out of a six-edge repair budget; no change was made to the live
state. Error reduction on this *activity proxy* was 32.5%, not 32.5% higher
intelligence, recovered facts, real-world task accuracy or biological healing.
Training was a short two-hot synthetic cycle (160 steps), fingerprint capture
72 steps, holdout 96 steps with separate random noise at amplitude 0.1.
The holdout is distinct but **not a new task or independent problem family**;
this pilot must not be used to assert out-of-distribution generalization.
The intact network exists only in the evaluator, not in the repair function.

**Tests added:** 9 for fingerprint validation/search/real-brain compatibility;
together with earlier 26 tests, **35/35 candidate tests passed** locally on
Python 3.13. Full legacy CI and actual SHA-pinned checkout validation remain
blocked by lack of container GitHub DNS and unresolved issue #6 (public commit
metadata privacy). Neither the fingerprint nor a supervisory controller is
currently wired into the uninterrupted v0.4 SQLite brain lifecycle; full
self-repair must not be claimed until validated and persistently integrated.

**Next:** improve task-level learning/retention under damage, enforce separate
validation and OOD test sets, implement fault detection and privacy-preserving
functional-signature persistence, then run controlled recovery with rollback
on the real persistent brain. Reward actual recovery, not number of new neurons.
