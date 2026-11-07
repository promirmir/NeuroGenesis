# Research protocol: falsifiable progress, not anthropomorphic claims

## Question

Does controlled structural plasticity improve **out-of-distribution learning or retention** over a matched fixed-structure network under equal training data and compute budgets?

## Current experiments (v0.2)

`python -m neurogenesis compare --steps 128` runs two deterministic instances receiving precisely the same input sequence. Growth is switched ON for one and OFF for the other. It reports structural and activity telemetry only. It is a **control harness**, not proof of intelligence, improved learning, consciousness or biological accuracy.

`python -m neurogenesis predict --steps 600` performs online one-step-ahead prediction on an alternating, in-distribution stimulus. The output is scored before seeing the next stimulus (prequential evaluation). The first/last window MSE should fall for both growing and fixed architectures; whether structural growth **helps** is not established. The reference constant-0.5 baseline has MSE 0.25. This is not an out-of-distribution test.

Re-run on Python 3.11, 3.12 and 3.13; every experiment must record code commit, configuration, seed, sequence, measured metrics and any deviations.

## Implemented pilot (v0.3)

`python -m neurogenesis benchmark --seeds 10 --steps-per-phase 128 --probe-steps 48`
performs synthetic A-B-A task switching, evaluates A with a new noisy sample
stream on a cloned snapshot with **readout training frozen** (but neural
plasticity still active on the clone), and returns per-seed means and paired
bootstrap interval. The benchmark intentionally reports an unfavorable result:
structural growth currently raises the A-after-B MSE relative to fixed
structure by about 0.0031 on this task. The control is not parameter- or
compute-matched; the test does not demonstrate unseen-concept generalization.
The pilot is a partial step toward the next requirements, not their completion.

## Required subsequent benchmarks

1. **Learning transfer:** train on repeated cue→target associations, test on disjoint cues and altered noise levels. Compare prediction accuracy against equal-parameter static spiking networks, a simpler tabular model and a random predictor.
2. **Retention:** interleave tasks A and B and measure accuracy on task A after learning B (catastrophic forgetting).
3. **Ablations:** disable growth, pruning, synaptic weight updates, and novelty detection independently; no single method gets credit for changes caused by another.
4. **Compute:** measure runtime, peak resident memory, number of connections, and hardware energy where instruments exist. The current energy proxy is *not* hardware energy.
5. **Replication:** compare across >=10 predeclared seeds, report distribution and uncertainty intervals, publish failed runs and exclude no results without documented criteria.
6. **Functional self-model:** test calibration of its own memory/capabilities against externally measured ground truth, including deliberately missing data and contradictory sources.
7. **Language grounding:** only after credible semantic grounding exists, evaluate responses against evidence from controlled text corpora; separate language-adapter performance from the neural substrate.

## Go/no-go decisions

- **No claimed learning improvement** until an independent evaluation dataset and matched controls exist.
- **No claimed generality** from simple toy tasks.
- **No claimed self-awareness or consciousness** from autobiographical memory, self-reports or computed introspection. Subjective consciousness lacks an accepted definitive operational test.
- **No automatic self-rewrite** promoted to live operation without isolated experiments, tests, rollback and human authorization for code deployment.

## Next milestone

Add independent held-out generalization, online task-switching and forgetting benchmarks, compare equal-parameter controls and quantify growth ablations, then introduce a Torch/CUDA implementation **only if** it preserves correctness against the reference CPU simulation and demonstrably improves performance.
