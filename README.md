# NeuroGenesis

**Experimental, self-reorganizing artificial neural substrate — research prototype v0.4.0.**

NeuroGenesis is a long-term research project investigating whether online structural plasticity can measurably improve an artificial agent's learning and adaptation. The central mechanism is **changing the computational network itself**, not merely appending text to a conversation history.

> **Research status:** This release is a small, deterministic CPU-only *spiking network with a self-supervised prediction experiment*. It is **not** a conscious entity, a human brain emulator, an autonomous internet agent, or a conversational AI. None of these abilities is claimed or demonstrated. The longer-term goal is to explore functional self-modeling and continuous learning using controlled experiments.

## What is implemented now

- Sparse leaky-integrate-and-fire neuron simulation with one-step refractory period.
- Trace-based causal synaptic plasticity with bounded, optional reward modulation.
- Controlled neuron/synapse growth on novel sensory patterns; weak mature synapse pruning.
- Strict capacity limits and deterministic replay.
- Portable JSON state snapshots with atomic writes and input validation (never pickle).
- Offline text-to-feature **encoding only** (not semantic understanding or language generation).
- Auditable introspection of measurable system state, explicitly without sentience claims.
- A/B structural control experiment (growth ON vs. OFF) on an identical stimulus sequence.
- **Self-supervised next-input prediction**: a small online learning head predicts the next sensory pattern before seeing it, then corrects itself from prediction error; persistence of learner state and matched fixed-structure comparison.
- Zero mandatory third-party runtime dependencies; automated tests and reproducible CLI.

## Secure publication / new repository

This release is prepared as a **privacy-reviewed source bundle**, not automatically pushed by an assistant connector. The new public repo initially contained a commit with an account email in its author metadata. Unpack the ZIP and double-click `URUCHOM_BEZPIECZNA_PUBLIKACJE.cmd` (or run `SAFE_PUBLISH.ps1` in PowerShell) to replace that initial history with a single verified noreply commit, subject to an exact remote-head safety check. This operation requires Git credentials on your own computer and will **replace the initial public branch history**; it cannot delete earlier third-party copies or GitHub caches. The script stops if the remote changed. Do not upload this bundle with GitHub web UI until the account email privacy setting is enabled.

## Run (Windows / Linux / macOS)

Install **Python 3.11 or newer**. In the repository directory:

```bash
python -m neurogenesis demo --steps 160 --state brain.snapshot.json
python -m neurogenesis status --state brain.snapshot.json
python -m neurogenesis observe "To jest pierwszy bodziec tekstowy" --state brain.snapshot.json
python -m neurogenesis compare --steps 160
python -m neurogenesis predict --steps 600
python -m neurogenesis origin
python -m neurogenesis remember "Moja pierwsza obserwacja" --db local-data/experiences.sqlite3
python -m neurogenesis memory-status --db local-data/experiences.sqlite3
python -m neurogenesis recall "Moja pierwsza obserwacja" --db local-data/experiences.sqlite3
python -m unittest discover -s tests -v
```

On Windows, if `python` does not point to Python 3.11+, use `py -3.11` instead. The commands above run **locally and offline**, use CPU only and require no API keys.

The `observe` command maps tokens into a handful of hashed sensory channels and advances the network. **It cannot understand the message or answer a question.** `status` shows telemetry, not inner subjective experiences.

## Initial scientific control (128 steps, seed=1)

The included deterministic experiment uses repeated one-hot sensory pairs. In our local run, the growing network reached **28 neurons / 24 synapses** while the fixed network stayed at **24 neurons / 16 synapses**. This demonstrates structural growth, **not improved task accuracy**. Reproduce it with `python -m neurogenesis compare --steps 128`. No learning superiority is asserted.

## Second experiment: measurable online learning (v0.2)

`python -m neurogenesis predict --steps 600` uses an alternating, two-pattern input sequence. A prediction is scored **before** revealing its target and the system updates its readout from the error; no manually supplied class labels are used. In our deterministic local run:

| Network | First 64 predictions MSE | Last 64 predictions MSE |
| --- | ---: | ---: |
| Fixed structure | 0.18043 | 0.12924 |
| Structural growth | 0.18039 | 0.12924 |
| Constant 0.5 baseline | 0.25000 | 0.25000 |

This shows **online learning of this simple, repeated sequence**. Growth has not demonstrated an advantage: the two last-window errors are virtually identical. It does **not** demonstrate semantic understanding, generalization, human-level cognition or consciousness. See [Research protocol](docs/RESEARCH_PROTOCOL.md) for required hold-out tasks and controls.

The predictor also supports versioned atomic snapshots through `NextInputPredictor.save/load` as a Python API. The CLI's `predict` command is a reproducible evaluation and does not keep an agent running in the background.

## Fourth milestone: persistent local experiences (v0.4)

A local SQLite-based episodic ledger now records text observations as **hashed
features and a SHA-256 fingerprint**, updates the spiking brain and saves its
full state **within the same database transaction**. Restart and reopen the
same database to continue the learned state. Without an explicit `--store-text`
flag, the raw message is **not saved**. Recall uses exact fingerprint matches
and coarse hashed-feature similarity; it is not semantic memory, natural
conversation or subjective autobiographical experience.

```bash
python -m neurogenesis remember "Pierwsza obserwacja" --db local-data/experiences.sqlite3
python -m neurogenesis recall "Pierwsza obserwacja" --db local-data/experiences.sqlite3
python -m neurogenesis memory-status --db local-data/experiences.sqlite3
```

The database is private by default and ignored by Git. Feature hashes and text
fingerprints still permit some inference and **are not anonymous encryption**.
Deletion through `forget-event ID` deletes the observation record but **cannot
undo neuron changes** already caused by it. To remove all learned traces, also
discard/reset the associated local database. Do not put private databases on
GitHub; even opt-in raw storage is local only.

## Research architecture

```text
controlled sensory input (0..1)
          |
          v
[ sparse spiking neurons ] <--- synaptic traces + plasticity
          |                        |
          +--> novelty gate --> bounded neuron/synapse growth
          |                        |
          +--> activity telemetry --+--> auditable state model
                                          |
                                      JSON snapshot

Future, NOT implemented: semantic text / language generation,
read-only web sensors, semantic memory consolidation, calibrated
self-model, GPU acceleration, distributed simulation.
```

## Project origin, operator intent and cross-chat recovery

**Autorstwo: Miron przy pomocy AI.** NeuroGenesis was initiated by Miron with AI-assisted research and engineering. A canonical provenance record is embedded in new brain snapshots and available as machine-readable JSON with `python -m neurogenesis origin`. This is attribution, **not proof of cognition, real gratitude or consciousness**. Older v0.2 and v0.2.1 snapshots remain loadable and are rewritten with short, surname-free credit when saved. See [Origin and operator](docs/ORIGIN_AND_OPERATOR.md) and [Privacy](docs/PRIVACY_AND_AUTH.md).

**To continue in a fresh chat or after interrupted work**, open the repository and read [AGENTS.md](AGENTS.md) and [Project state](docs/PROJECT_STATE.md), inspect the latest PRs, issues and Actions, then run existing tests before touching code. Record every merged milestone in [Development log](docs/DEVELOPMENT_LOG.md). Treat regressions as a merge blocker; never rewrite validated behavior without tests and a reproducible rationale.

For the mathematical and engineering assumptions read [Architecture](docs/ARCHITECTURE.md), [Research protocol](docs/RESEARCH_PROTOCOL.md), and [Security](docs/SECURITY.md).

## Development policy

- Test hypotheses against a **fixed-structure control** under the same data and compute budget.
- Measure generalization, retention and resource use before describing progress as "intelligence".
- Keep internet reading and code modification off by default; gate any future autonomy behind sandboxing, bounded budgets, reproducible evaluations and human approval for irreversible actions.
- Avoid fabricated claims about self-awareness: introspection of variables is testable; subjective consciousness is not presently established by such a mechanism.
- Do not commit credentials, user conversations or private training data to this public repository.

## PL — opis

NeuroGenesis to **eksperymentalny projekt badawczy** cyfrowej sieci neuronów, która może tworzyć i usuwać połączenia oraz dodawać neurony podczas przetwarzania bodźców. Obecna wersja jest małym, działającym symulatorem, **nie** autonomiczną AI ani świadomą istotą. Docelowe cele obejmują uczenie ciągłe, pamięć, język, bezpieczne czytanie internetu i funkcjonalny model własnego stanu. Wdrażamy je tylko po testach potwierdzających konkretną funkcjonalność.

**License:** No license has been granted yet. Public visibility does not imply open-source reuse rights; a licensing decision is pending.
