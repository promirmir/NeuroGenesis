# Autonomous self-development: bounded experimental candidate

**Status: local research candidate, NOT merged or integrated with the live Windows UI.**
Public credit: Miron przy pomocy AI.

## What exists

The new `neurogenesis/self_development.py` autonomously proposes a small, bounded portfolio of changes to the **actual** v0.4 next-input neural predictor: readout learning rate and STDP-like synaptic plasticity rate. It clones the state, trains each candidate on the same observed samples, selects on one dataset and audits the single top challenger on a separate dataset. A prior-skill guard rejects changes that degrade previously learned behavior beyond a stated threshold. The original neural state remains untouched until a successful candidate is explicitly promoted by the surrounding controller. Rejected changes return an identical restored state.

The engine does not alter source files, network settings, security settings, authentication, arbitrary memory rows or external services. There are no claims of semantic language understanding, human-brain equivalence or self-awareness.

## Decision protocol

1. Freeze and clone a valid `NextInputPredictor` state from versioned storage.
2. Generate at most five bounded policy candidates: incumbent, faster/slower predictive readout and stronger/weaker local synaptic plasticity.
3. Replay a bounded, finite set of already authorized sensory samples; evaluate predictive MSE on fresh selection samples, with no readout training during scoring.
4. Select the best challenger if it beats the **equally trained incumbent** by the predeclared `min_gain`; enforce neuron/synapse count caps.
5. Evaluate that single challenger once on **independent, previously unused audit data**, then check a protected retained-skill stream. Any failure causes rollback to an exact clone of the original pretrained state.
6. On success, return the trained candidate state to the caller. Persistence/promotion to the live process is deliberately **not yet implemented**. A separate privileged supervisor must atomically checkpoint and coordinate it with private SQLite state before it becomes a continuous background feature.

### API example

```python
from neurogenesis.self_development import run_self_development_cycle

# current: a real, already loaded NextInputPredictor
# training / selection / audit / retained_skill: independent sequences
candidate, report = run_self_development_cycle(
    current, training=training, selection=selection,
    audit=audit, retained_skill=retained_skill
)
if report["promoted"]:
    # Candidate is an isolated proposed state, NOT automatically installed.
    # Human-controlled integration must provide atomic persist/rollback.
    pass
```

## Anti-regression and limitations

- This is a limited hyperparameter-search mechanism, not open-ended autonomous intelligence. It can make choices about parameter settings without receiving human instructions for every candidate; it does **not** invent new learning algorithms.
- Using the same pattern family with independent noise seeds does not prove out-of-distribution generalization. Evaluators must use genuinely new tasks and compare neural/no-neural and compute-matched baselines.
- The v0.4 predictor's `learn=False` stops **readout** learning but still advances STDP in an isolated cloned brain. A future strict inference-only neural probe is required.
- Use fresh, never-reused selection and audit sets each time. A check prevents exactly identical streams but cannot prove causal independence or prevent the caller from recycling past samples.
- Every candidate is sampled from a fixed, bounded family. Multiple cycle promotion using recycled audit data would be methodologically invalid and must be blocked in the eventual persistent controller.
- The current candidate does not automatically run on a schedule, persist accepted updates in SQLite, or self-edit code. These need additional work, security gates and independent evaluation.
- Existing `Brain` / `NextInputPredictor` snapshot schema is unchanged. Validating compatibility with all 41 original CI tests and building the EXE require an actual checkout and Windows runner.

**Release gate:** privacy issue #6. Until controlled noreply commit metadata can be guaranteed, do not create new public source commits through connector APIs without explicit identity control.
