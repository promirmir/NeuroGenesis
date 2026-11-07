# NeuroGenesis Foundation Brain — scalable, trainable core

**Credit: Miron przy pomocy AI.**

## Why the architecture changed

The verified v0.5.6 Windows app is a useful private, deterministic,
small spiking-network/SQLite prototype, but eight hashed sensory channels
and 24 initial neurons cannot represent the complexity of natural language.
The bag-of-words hash loses token order and creates many collisions.
Adding rules or neurons incrementally does not produce general intelligence.

Original LIF code and the preserved (not merged) PR #17 remain as
reproducible experimental baselines. See issue #18. The stable Windows EXE
and the user's existing SQLite data must not be replaced or corrupted.

## New trainable neural foundation

The new optional module neurogenesis/foundation.py is an actual PyTorch
neural network trained on ordered input, not a wrapper around any
external pretrained LLM and not a database of predefined answers.

- Ordered UTF-8 byte tokens (256 symbols), preserving word order.
- Learned trainable embedding into a configurable hidden state.
- Fast recurrent cortex: multi-layer fused GRU learning temporal dynamics.
- Slow recurrent cortex: an additional GRU summarizing completed chunks,
  visible only to later chunks (causal next-token prediction).
- Self-supervision: next-byte cross-entropy plus auxiliary prediction of
  the next learned latent state with detached target.
- Configurable parameter ceiling, bounded sequence/batch length and
  clipped gradients; operator retains control over resource use.
- Atomic, versioned checkpoint storing numerical model weights.
- Local training script with explicit user-selected, licensed or owned
  corpus. No crawlers, no external API calls, no download of models.

**Biology qualification:** GRU networks have mathematically specified
state dynamics and two time scales; they are not faithful simulations of
the human cerebral cortex. The old LIF module can be incorporated only
after a controlled neural-ablation experiment shows real value.
These choices draw on multi-timescale neurocognitive principles, without
claiming human brain equivalence or consciousness.

The new model is designed for CPU/GPU scaling but **does not yet produce
intelligent language**. Untrained parameters are meaningless. First
train it with adequate data, then test transfer, retention and grounding.

## Controlled local training

The main Windows executable does not need PyTorch and stays unchanged.
For research training on operator-selected data:

    pip install -e ".[foundation]"
    python -m neurogenesis.foundation_train --input corpus.txt \
      --output local-foundation.pt --confirm-corpus-rights \
      --device auto --hidden 128 --fast-layers 2 --slow-layers 1 \
      --chunk 16 --sequence 64 --steps 100

The command limits its input corpus to 32 MiB for the initial pilot,
requires an explicit rights acknowledgment, and never collects network
information. CUDA is used only if available. The simple chronological
holdout is not equivalent to generalization outside the data distribution.

A default foundation model contains a few million parameters, not billions.
Next tiers can target 10M, 50M and 100M+ **only if independent tests show
benefit per unit compute and the user approves resource limits**.
GPU VRAM, throughput and numerical parity must be measured on hardware.

## Independent acceptance requirements

1. GitHub foundation-cpu.yml must install actual PyTorch (not silently
   skip all tests) and verify tensor dimensions, causal masking, fast/slow
   gradients, real loss reduction, byte-order preservation, validation,
   replayable checkpoints and explicit corpus permission.
2. Test on independently sourced, rights-respecting natural text with
   strictly separate training/validation/audit documents.
3. Compare with a fixed-size simple GRU, a small Transformer, Markov
   baselines, and disabled slow-state / latent-loss ablations at matched
   parameter and compute budgets. Report seed variation.
4. Assess context retrieval, long-horizon prediction, task transfer,
   forgetting, latency, RAM, VRAM, tokens/s and failure cases.
5. Retain old memory snapshots and Windows one-click interface. Only
   connect a tested, usable GPU worker and private checkpoints after
   inference, failure recovery and user resource controls are verified.
6. Do not claim cognition, human brain simulation or autonomous code
   invention based on a reduction in synthetic token prediction loss.

## Research basis

- Dao and Gu, ICML 2024, Transformers are SSMs:
  https://proceedings.mlr.press/v235/dao24a.html
- Assran et al., 2025, V-JEPA 2:
  https://ai.meta.com/research/publications/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning/

These are architecture and evaluation references; the initial GRU is
NOT a reproduction of Mamba-2, V-JEPA 2, or a frontier-scale model.
