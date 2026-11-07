# Architecture — v0.2 research core

## Scope and scientific assumptions

This is an **engineering baseline**, not a faithful cell-by-cell emulation. Each neuron is a single-compartment leaky integrate-and-fire unit. Synaptic weights are nonnegative (excitatory only); refractory timing is one step; time has no calibrated biological units. The deterministic input encoder is a fixed hash, **not** semantic language understanding. All of these restrictions are explicit and will need revision before biological realism claims.

## Discrete-time model

For neuron *i* at tick *t*, absent refractoriness:

```text
I_i(t) = g * s_i(t) [for sensory neurons] + sum_j w_ji(t) * z_j(t-1)
V_i(t) = alpha * V_i(t-1) + I_i(t)
z_i(t) = 1 if V_i(t) >= threshold else 0
```

After firing, voltage resets to 0 and the cell remains refractory for one tick. Trace `q_i(t) = min(5, beta*q_i(t-1) + z_i(t))`. Updates use the **previous** traces to preserve causal direction:

```text
Delta w_ij = eta * (1 + reward) * (
    q_i(t-1) * z_j(t) - 0.25 * q_j(t-1) * z_i(t)
)
w_ij <- clamp(w_ij*(1 - decay) + Delta w_ij, 0, weight_limit)
```

The reward parameter is an optional external scalar in [-1,1]. No source of intrinsic human motivation is asserted. This is a heuristic trace update; it has **not** been calibrated against biological STDP data.

## Structural plasticity

Novelty is the minimum mean absolute feature distance to a bounded dictionary of previously observed sensory patterns. When sufficiently novel input has been encountered, at each structural update interval the system may add one neuron and two synapses. Growth is limited by `max_neurons` and `max_synapses`. Weak synapses older than `prune_min_age` are pruned at the same interval.

The growth policy is intentionally simple and falsifiable. It is **not** equivalent to neurogenesis or axonal growth in tissue. Capacity constraints limit CPU and snapshot use. The sparsely stored synapses produce an O(E+N+P*d) update per step, where E is synapses, N neurons, P retained patterns, and d input dimensions.

The measured `energy_proxy` equals number of spikes plus 0.001 times active synapse count per tick. This is a reproducible *proxy*, never physical joules or power consumption.

## Determinism and state integrity

All pseudorandom initialization uses a specified 32-bit LCG with serialized state. Snapshots include neurons, potentials, traces, synapses, remembered patterns, and learning counters. JSON snapshots use a versioned schema, bounded size and strict shape/range validation; saves use a temporary file, `fsync` and atomic replacement. Reloading and replaying the same stimuli produces the same results by design.

This format is not encrypted, authenticated or a secure place for sensitive information. Backups and file permissions are the user's responsibility.

## Modules

- `brain.py`: neuron dynamics, causal plasticity, structural growth, pruning, telemetry, serialization.
- `sensory.py`: deterministic hash-bucket text signals; deliberately limited to feature encoding.
- `self_model.py`: auditable state description, never claims of subjective experience.
- `experiment.py`: matched-input structural comparison.
- `predictor.py`: causal online prediction head trained by its own next-input error, an A/B control, and a separate versioned learner snapshot.
- `__main__.py`: local offline commands for demonstration and state inspection.

## Development boundaries

Language, self-initiated research, browser access, lifelong generalization, multi-machine execution, GPU acceleration and self-modifying code are **future research tasks**, not available capabilities in v0.1. A language model may eventually act as an interface, but the biological research core must be evaluated separately so that improvements are not falsely attributed to it.

## Self-supervised online prediction (v0.2)

After observation *t*, the network trace vector `q(t)` is clipped to `[0,1]` and used as the readout's feature vector. A logistic linear head predicts input *t+1*. On arrival, we compute its **pre-update mean squared error**, then take one bounded normalized gradient step on the head weights and bias. When the substrate adds a neuron, the corresponding new readout weights start at zero. The snapshot includes the readout and its pending prediction, allowing exact reproducible continuation.

The online head is learned; the feature encoder remains simple and the recurrent substrate follows separate heuristic plasticity. This test demonstrates prediction on a tiny repeating sequence only. The growing and fixed-substrate variants have essentially equivalent prediction errors, so **this experiment does not establish an advantage from growth**. No language, reasoning or sentience is implied.
