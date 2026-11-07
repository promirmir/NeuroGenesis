# NeuroGenesis — functional skill recovery benchmark v0.5.2 (candidate)

**Public credit:** Miron przy pomocy AI.

## Scientific question

Does memory-guided reconstruction of lost synaptic connections recover an **actually learned next-sensory-step predictive behavior**, rather than merely making hidden spike traces resemble a pre-injury signature?

## Experimental design

Command:

```bash
python -m neurogenesis.skill_recovery --seeds 20 --fraction 0.5 --train-steps 600 --probe-steps 96 --noise 0.1
```

The model trains on 600 alternating paired 8-channel stimuli, using the real v0.4 spiking brain and its adaptive readout. The brain is held at fixed size to isolate damage and repair. An isolated clone records 72 steps of the pre-injury **hidden activity fingerprint**; it is not given future holdout target vectors or intact network topology. A deterministic 50% synaptic lesion is applied on a clone, and a bounded greedy compensatory search can add at most six synapses to reduce the recorded activity mismatch. A further fresh 96-step noisy stimulus set measures next-input prediction MSE before any readout weight updates. Intact, damaged and repaired copies use identical learned readout weights. A separate two-pattern held-out test uses **disjoint channels 4–7**, rather than merely adding noise to seen channels 0–3. A non-neural Markov model and constant-0.5 predictor are included.

The readout is frozen during tests, **but the existing v0.4 `Brain.step` still updates spiking-network synapses** inside isolated test clones. A separate strict synaptic-plasticity-off probe remains a required next improvement. Neither test environment has actual text comprehension.

## Independently reproduced local candidate outcomes

For Python 3.13, 20 seeds, 600 training steps, 96 scored holdout transitions, Gaussian-free uniform bounded noise ±0.1:

| Random synapses removed | Mean intact MSE | Mean damaged MSE | Mean repaired MSE | Improved seeds | Mean new connections |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0% | 0.11433558 | 0.11433558 | 0.11433558 | 0/20 | 0.00 |
| 10% | 0.11433558 | 0.11458848 | 0.11442895 | 5/20 | 0.25 |
| 25% | 0.11433558 | 0.11492475 | 0.11446319 | 11/20 | 0.65 |
| 50% | 0.11433558 | 0.11585211 | 0.11446229 | 17/20 | 1.45 |

At 50% synaptic loss, the mean MSE deterioration due to damage was 0.00151653 and repair reduced the mean error by 0.00138982. This is **~91.6% of the damage-induced error increment recovered**, not a 91.6% reduction of total error. The paired conditional bootstrap 95% interval for that gain is **[0.00092813, 0.00185162]** under this narrow fixed-seed experiment. In the remaining 3/20 seeds there was no gain, and no seed was worsened in the selected test. This does not imply recovery on unseen tasks.

**Critical negative control:** the simple non-neural Markov model scored **MSE 0.00166894** on the same in-distribution holdout, far better than the current learned neural readout (MSE 0.11433558), without needing a neuron network. On disjoint-cue holdout, mean damaged MSE at 50% loss was **0.23955236**, repaired **0.23964903** (slightly worse), and Markov **0.22663844**. **NO-GO for any claim that the present architecture generally beats simple alternatives or transfers learned skills to unseen input patterns.**

## Reproducibility and privacy

The local test set uses a reconstructed, interface-compatible subset of upstream v0.4, **not a verified byte-identical clone**. Existing GitHub `main` SHA at evaluation: `46b75ccf2badf746756b36a5a382f69da0598ce8`. Do not claim these candidate tests were run in its CI. All additions are new filenames; no changes to v0.4 brain/SQLite snapshot formats are required for this candidate.

Until issue #6 is fixed, no GitHub source write is permitted through a connector that cannot explicitly guarantee noreply identity. The Windows build workflow intentionally invokes strict metadata scanning and must fail on old privacy-unsafe history, rather than suppressing the check to manufacture an EXE.

## Next research implementation

1. Add a strictly inference-only spiking step (no mutation of synaptic weights, growth, novelty patterns or counters in **source** brain; cloned dynamic membrane may progress) and compare freezing effects.
2. Learn useful state representations and temporal predictive connections, then compare to non-neural controls with equal resource budgets; reducing artificial network size is not a failure if it improves generalization.
3. Extend recovery to held-out independent tasks, not just repeated two-cycle patterns; use at least 10 preregistered seeds, paired resource/compute measurements and out-of-distribution shifts.
4. Attach homeostatic regulator to continuous lifecycle without losing transactionality or original SQLite brain state; keep internet OFF until a separate validated security transport exists.
5. Verify all 41 original tests in actual clean clone plus candidate tests on Python 3.11/3.12/3.13, build `NeuroGenesis.exe` in Windows Actions with real GUI smoke test, and publish only with privacy-safe Git metadata.
