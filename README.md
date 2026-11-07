# NeuroGenesis

### Windows — pobierz najnowszą wersję EXE

[**Pobierz NeuroGenesis.exe — Windows x64**](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe) · [SHA-256](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256) · [Strona najnowszego wydania](https://github.com/promirmir/NeuroGenesis/releases/latest)

**Jedno kliknięcie, bez instalowania Pythona.** Program jest eksperymentalny i niepodpisany cyfrowo. Zweryfikuj pochodzenie i SHA-256; lokalna pamięć pozostaje w katalogu użytkownika po aktualizacji. **Internet pozostaje wyłączony**, a panel nie jest jeszcze rozumiejącą język AI.


**Experimental, self-reorganizing artificial neural substrate — research prototype v0.5.7.**

NeuroGenesis is a long-term research project investigating whether online structural plasticity can measurably improve an artificial agent's learning and adaptation. The central mechanism is **changing the computational network itself**, not merely appending text to a conversation history.

> **Research status:** v0.5.7 includes the original small deterministic CPU spiking brain, local SQLite persistence, a native Windows desktop application and optional experimental neural regulation/repair/capacity experiments. The self-development controller now supports **opt-in periodic local trials with transactional promotion and rollback**, but it is not a self-coding agent or general-intelligence system. Capacity experiments remain bounded offline trials. This is **not** a conscious entity, a human brain emulator, a natural-language conversational AI, a working internet crawler, a GPU neural implementation or a claim of general intelligence.

## Automatyczne uczenie kontekstu (v0.5.7)

Każda nowa wiadomość uruchamia **samodzielne uczenie przewidywania następnego bodźca** na podstawie bieżących i poprzednich danych sensorycznych oraz rzeczywistych śladów neuronów impulsowych. Nie trzeba ręcznie podawać odpowiedzi, żeby model ten aktualizował własne wagi. Na zakładce **Mózg** widać liczbę przejść i błąd MSE. Uczenie kontekstu i stan mózgu zapisują się w tej samej lokalnej transakcji SQLite, bez zapisu surowego tekstu przy zwykłych wiadomościach. Kontrolowane eksperymenty porównują warianty z pamięcią, bez pamięci oraz z odłączonym odczytem neuronowym. **To uczenie sekwencji, nie semantyczne rozumienie języka ani autonomiczne generowanie odpowiedzi.** [Opis matematyczny i ograniczenia](docs/CONTEXT_LEARNING.md).

## Pierwsze działające uczenie dialogowe (v0.5.6)

W zakładce **Rozmowa** wpisz pytanie, poniżej podaj odpowiedź i kliknij **Naucz odpowiedzi**. Przy kolejnym wysłaniu tego samego pytania NeuroGenesis odtworzy nauczoną odpowiedź z lokalnej bazy. Pytanie równocześnie aktualizuje własną sieć neuronową. Poprawiaj lub usuwaj odpowiedzi przyciskami w oknie. **To jawne zapamiętywanie skojarzeń, nie samodzielne rozumowanie neuronów ani generowanie języka.** Pełny tekst pytania i odpowiedzi jest zapisywany jedynie po jawnym kliknięciu przycisku nauki. Więcej: [instrukcja nauki](docs/TEACHABLE_DIALOGUE.md).

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
- Additive v0.5.4 research modules: bounded homeostasis, experimental memory-guided rewiring, held-out task-recovery evaluation, simple Markov control, resource budgets and selection/audit-gated self-development experiments. These are **not automatically running** in the GUI or current persistent memory loop.
- Native Tkinter Windows interface with automatically adapting temporal-context prediction readout over real spiking-neuron traces, plus explicitly taught question/answer recall, brain statistics and Internet OFF; PyInstaller single-EXE workflow.
- **v0.5.5:** opt-in bounded periodic self-development supervisor, 40 fresh sensory events per trial, separate training/selection/audit/retention inputs, atomic preservation of a single brain + predictor in SQLite, failure rollback and checkpoint safeguard. This is not evidence of semantic conversation; see [implementation and limitations](docs/AUTONOMY_SUPERVISOR.md).
- Zero mandatory third-party dependencies when running the Python research core; automated tests and reproducible CLI.

## Windows: one-click executable

1. Download the latest verified [**NeuroGenesis.exe**](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe) from [GitHub Releases](https://github.com/promirmir/NeuroGenesis/releases/latest). No Python installation or terminal required.
2. Optionally download the [SHA-256 checksum](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256) and compare it with `Get-FileHash .\\NeuroGenesis.exe -Algorithm SHA256` in PowerShell.
3. Double-click `NeuroGenesis.exe`. The native app provides Rozmowa / Mózg / Internet tabs, including optional bounded self-tuning (AUTO is OFF by default). Text is treated as sensory input, not demonstrated semantic comprehension. Internet is OFF.
4. The database lives under `%LOCALAPPDATA%\\NeuroGenesis\\experiences.sqlite3` independently of the EXE. Do not delete it during upgrades; maintain private backups. It is not encrypted.

After successful Windows build+SQLite smoke tests on **main**, a separate, minimally scoped GitHub Actions workflow verifies the SHA-256 checksum and publishes the binary plus checksum as a versioned GitHub Release, without executing pull-request code with release-write privileges. Release tags include the source commit prefix for reproducibility. Temporary Actions artifacts remain available for debugging. The Windows EXE is **unsigned and experimental**; verify its checksum and security warnings. See [Polish quickstart](URUCHOMIENIE_PL.md) and [build notes](docs/WINDOWS_EXE.md).

## GitHub publication and privacy

The working source is published on `main` through [PR #10](https://github.com/promirmir/NeuroGenesis/pull/10); **do not run old fresh-root history-rewrite instructions or force-push this repository**. Public attribution: **Miron przy pomocy AI**. Author/committer display names and sources must not expose a surname, credentials, local user paths or private content. The repository operator explicitly accepted account-email visibility in Git commit metadata; the optional strict-email audit is therefore not a merge prerequisite. Run `python -m scripts.privacy_audit --git` and review CI logs.

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
