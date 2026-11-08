## 2026-11-08 — EMBODIED PRESENCE / FOUNDATION LAB 0.9.0 — release candidate

- Work on `feat/avatar-foundation-lab-20261108`, based on merged holographic LIF source `d54eb6d2b4c7dd97eef63032a7940c7cff5f32dd`. This is the REAL `desktop.py` → Windows onefile Tk EXE path, NOT another optional-only Qt demo. Public download is previous release until verified post-merge.
- `neurogenesis/tk_avatar.py`: futuristic humanoid 2.5D avatar, **symbolic** physical-looking representation. Only a new actual stored LIF step triggers an activity ring, and actual fired neurons trigger eye response. Camera/HUD idle motion is clearly distinct. Dashboard switches among authentic existing 2D, orbital 3D and avatar. No microphones, voice, camera, inference of consciousness or hidden network.
- `neurogenesis/tk_foundation_lab.py`: actual Foundation Brain next-byte greedy prediction in a user-selected isolated external Python environment with installed PyTorch/neurogenesis, local operator-trusted trained numerical checkpoint and explicit consent. Because frozen Tk EXE does NOT ship torch, no automatic downloads or false claim of built-in neural language intelligence. Private prompt piped on stdin; no argv exposure. CPU/CUDA manual and 1-64 byte bound, worker subprocess cancellable, no source mixing, no persistent writes, no automatic weights promotion.
- `neurogenesis/foundation_infer.py` adds CLI `--prompt-stdin`; optional prior `--prompt` retained; bounded input 2048 UTF-8 bytes. Unit tests `tests/test_tk_avatar.py`, `tests/test_tk_foundation_lab.py`, Windows real Tk widgets in `tests/test_tk_mission.py` and actual `desktop --ui-self-test` updated. Docs `docs/EMBODIED_FOUNDATION.md`.
- Version 0.9.0 in `pyproject.toml` and `neurogenesis/__init__.py`. No SQLite migration; old config and private data remain unchanged, still research prototype.
- **RELEASE GATES:** all Python 3.11–3.13, privacy, Windows Tk + actual frozen EXE `--self-test`/`--ui-self-test`, Qt Windows/Ubuntu, real CPU Torch, inspect synthetic screenshot and verify official 0.9.0 SHA-bound GitHub Release. Do not claim completed AGI or competent model chat.

## 2026-11-08 — HOLOGRAPHIC CORE development candidate, not released

- Feature branch `feat/holographic-neural-core-and-capacity-20261108`, preserving confirmed 0.8.0 Windows release and all local user memory. Actual public EXE is still Tk; 3D-like orbit is implemented IN the default Tk Mission, not only optional Qt.
- New pure telemetry-driven `neurogenesis/tk_hologram.py`: geometric camera rotates at 90ms only while mapped, new spike event wave only for increased saved LIF step; explicit symbolic topology disclaimer, bounded 144 nodes/360 synapses. Switch 3D/2D with original `TkConnectome` retained.
- New `BrainConfig` ceilings 512 neurons/4096 synapses/1024 patterns are for new memories ONLY; SQLite snapshot config is not silently migrated, initial count 24 remains, no measured performance/intelligence claim. Actual per-user ceiling is visible in UI.
- Tests: `tests/test_tk_hologram.py` for telemetry/projection/old memory, extended Windows Tk dashboard tests. New documentation `docs/HOLOGRAPHIC_CORE.md`.
- NOT YET RELEASED. Required: Python 3.11–3.13, privacy, PyTorch CPU, Qt Windows/Ubuntu, real Tk Windows GUI/frozen EXE smoke and post-merge source-verified release. Do not state the previous release includes these changes.

## 2026-11-08 — VERIFIED published default Windows Mission Control v0.8.0

- **Root cause fixed:** A user's screenshot showed that the last official onefile `NeuroGenesis.exe` displayed the old plain Tk chat, despite the separate optional Qt Mission Control already being source-tested. This was a delivery mismatch. PR #50 upgraded the **actual default public Windows application**, not just another non-distributed Qt prototype.
- **Merged code:** PR #50 into `main` `8e27f420613adee40b7f94b89760f1514284f743`. Official Release: [v0.8.0-main.8e27f420](https://github.com/promirmir/NeuroGenesis/releases/tag/v0.8.0-main.8e27f420). `NeuroGenesis.exe` Windows x64, 13,094,247 bytes, **SHA-256 `5e48e1c7ecde3b7a066a39c2b71c8a70764351888ff30dc23ba75b53c6fcb44e`**. Verified GitHub Actions post-merge research-core, dedicated real PyTorch CPU, Qt Windows/Ubuntu, public onefile Windows EXE and publisher checks all **SUCCESS**. The real frozen EXE successfully ran both old `--self-test` and new `--ui-self-test` with disposable SQLite and actual Tk widgets.
- **Now visible upon double-click:** fullscreen-capable native Tk Mission Control first tab with dark responsive layout, clear rather than grey notebook tabs, four true brain/knowledge metrics, visible connectome from real recorded LIF synapses, recorded spike trace, real-event journal and permission/memory/brain/Foundation module statuses. The legacy conversation interface was restyled to match, with distinct user/assistant text and visible composer. All old brain/research/memory/recovery functions retained; no database migration/reset or network startup. Window size now respects local screen dimensions; dashboard scrolls on small virtual/laptop screens.
- **Actual visual verification:** Windows CI captured and uploaded `NeuroGenesis-Tk-Mission-Visual` (synthetic only, genuine Tk screenshot; screenshot dimension 1000×676 on constrained hosted desktop), inspected and corrected small-screen clipping; this artifact previews the **dashboard pane**, not a screenshot of the full Tk tab chrome or a physical user laptop. Screenshots from earlier head may differ in layout slightly; exact final source head is `a362411aa555b9506983b055ed8c26e1b41c1b7f` and its Windows screenshot artifact is from that commit.
- **Still distinct:** The released `NeuroGenesis.exe` remains a **polished Tk interface**, not the more advanced optional PySide6/Qt binary. Public Qt EXE packaging remains gated by verified LGPLv3 notices, corresponding library source/source offer controlled by publisher, library replacement/relinking and full runtime license audit. Qt remains available via consent-first `Launch-NeuroGenesis-Mission-Control.cmd` from full repository with Python 3.12.
- **Scientific scope:** no general AI, model-level semantic conversation, brain reconstruction, physical CUDA performance demonstration or validated knowledge of factual entailment is established by this GUI change. LIF trace is not Foundation GRU internals. No fake learning indicators.
- **Follow-up:** do not again recommend downloading prior v0.7.x GUI when asked for the improved interface. Keep the correct v0.8.0 verified link/sha in docs. Avoid additional feature churn until users have validated the release on their own Windows/DPI environment. The historical candidate sections below are superseded by this verified heading.

## 2026-11-08 — VERSION 0.8.0 DEFAULT WINDOWS EXE GUI FIX, pending CI

- Important user-reported mismatch (screenshot): the official 0.7.0 `NeuroGenesis.exe` opened the **old Tk window with empty oversized conversation box**, despite earlier announcement of futuristic Qt Mission Control. Qt had only been tested in source and was **not** the published EXE. The messaging was misleading. This branch fixes the actual shipped front end rather than another demo.
- Source baseline `main` `c2db57b1ab1ef99927f8cd7e17d1b522ae78141e`. Branch `feat/default-exe-mission-dashboard-20261108` changes **default `desktop_launcher.py` → `desktop.launch`** by adding a new first and preselected `CENTRUM` tab with dark premium native Tk layout: true SQLite LIF neural fabric canvas, 4 measured KPI cards, recorded spike-mask trace, actual step-change journal, real SQLite/HTTPS/LIF and separate Foundation module status, navigation actions to preserved chat/brain/internet tabs. Dark readable notebook tab styles, 1450×920 startup, scrollable panel to accommodate lower resolution; no UI data fabrication, no empty chat first screen.
- New `neurogenesis/tk_mission.py` is standard-library Tk and uses **existing** proven `neural_telemetry.py` and `tk_connectome.py`, never touches users' private memories, creates no new database schema and no Qt dependency. Network stays disabled by default. `desktop --ui-self-test` starts **actual widgets** using only a throwaway synthetic SQLite; Windows CI runs it in Python and in the *real frozen public Tk EXE* in addition to existing read-only brain/SQLite smoke. `tests/test_tk_mission.py` verifies persisted steps/synapses, no fabricated idle events, updated real spikes, and network consent state on actual Windows Tk widgets.
- Update package and README metadata to **0.8.0**, including the explicit difference between distributable Tk Mission dashboard and optional richer Qt. Do not promise bundled Qt until independent LGPLv3 source/notice/relinking compliance. The LIF display is not a visual simulation of Foundation GRU or human intelligence; semantic natural QA performance remains an open scientific goal.
- Candidate must pass Python 3.11–3.13, privacy, real Windows source Tk widget tests, **actual frozen EXE --self-test AND --ui-self-test**, Qt Windows/Ubuntu regression and post-merge SHA-verified 0.8.0 release before marking delivered. Do not ask user to redownload 0.7.0: it retains the old default screen.

## 2026-11-08 — VERIFIED Mission Control UI integration (PR #48 merged)

- The new real-data **Qt Mission Control** is now in `main` commit `caa544798c5c20ac1cc7cb523e82a9593bd513f2` (PR #48 squash-merged). Feature head `68640020fed9509447f0b85267727354fd367e86` passed Python 3.11–3.13, privacy, Qt offscreen Windows and Ubuntu, Windows **frozen Qt technical build** and default **frozen Tk Windows EXE** regression. Screenshots rendered by the real Qt GUI using only synthetic, local SQLite were inspected on both Windows and Ubuntu; an early QSS issue with opaque QLabel text backgrounds and the Windows offscreen missing-font fallback were found and corrected. The latest verified Windows PNG has readable text.
- The unified dashboard features live LIF topology, recorded spike history, actual observation-step events, SQLite/doc/network/training status and navigation; real step-only highlights with an **illustrative** edge movement (not an actual axonal conduction speed); no fabricated GPU, AGI, or AI understanding metric. Existing source-cited chat, rights, local memory, opt-in crawler, candidate-only PyTorch training and verified backup are preserved. No local data migrated or reset.
- `Launch-NeuroGenesis-Mission-Control.cmd` launches the **real** Qt code on Windows from the full repository using a user-local Python 3.12 venv. It explicitly asks permission before downloading PySide6. This is a *source launcher*, **not** a public Qt installer or standalone EXE.
- The primary published `NeuroGenesis.exe` remains the legacy **Tk** app until a separately verified legally compliant Qt build: LGPLv3 notice/license/library source under distributor control and replaceable dynamic libraries, manual Windows DPI/accessibility acceptance and immutable source-SHA/asset checksum. Latest Qt Windows & Ubuntu screenshot files can be obtained from the PR #48 GitHub Actions run as the short-lived `Mission-Control-Visual-*` artifacts.
- Stale divergent `feat/live-neural-network-command-visualization-20261108` 0.8 branch remains **unmerged** and must not be silently squashed into main; it had version metadata CI failure and a separate older neural renderer. Keep it intact unless the operator explicitly asks for deletion. Full accepted scope and remaining barriers: [MISSION_CONTROL.md](MISSION_CONTROL.md).
- Full research goals remain **unfinished**: Foundation Brain is not a validated conversational model, current natural QA can falsely cite unsupported premises, real CUDA speedup and Qt compliant public release not demonstrated. This merge finishes a *substantial GUI implementation*, not AGI or v1.

## 2026-11-08 — nowy Mission Control Qt (PR kandydat, bez automatycznej dystrybucji)

- Bieżący `main` rozpoczęcia: `d5e0fcec24efd99f6363a6f09328141039023c24`, bez otwartych PR i z zielonymi testami źródeł Tk/Qt/Windows. Rozbieżna gałąź `feat/live-neural-network-command-visualization-20261108` miała 14 commitów ahead / 2 behind i czerwone Python CI (metadane 0.8 vs README 0.7); **nie scalać jej automatycznie, nie usuwać**.
- Nowa gałąź `feat/command-center-mission-control-20261108`: spójny ciemny układ Qt z 4 rzeczywistymi kaflami SQLite/LIF, dużym graficznym Neural Fabric również na głównym Dashboard, panelem realnych impulsów krok-po-kroku, dziennikiem zaobserwowanych zmian, rozdzielonymi statusami modułów HTTPS / SQLite / LIF / Foundation i nawigacją Ctrl+1…7. QPainter pokazuje tylko faktyczne neurony, synapsy, wagi i spiki; świetlne przejście (max 0,8 sekundy) tylko przy nowo zapisanym kroku. Droga światła jest **umowną animacją**, nie pomiarem szybkości impulsu.
- `Launch-NeuroGenesis-Mission-Control.cmd` uruchamia prawdziwy Qt ze źródeł przez prywatne Python 3.12 `.venv` i przed pierwszym pobraniem PySide6 prosi o zgodę; bez zmian w user SQLite lub autostartu HTTPS. To nie jest standalone EXE Qt.
- Dedykowany `scripts/qt_visual_smoke.py` renderuje prawdziwe Qt na **wyłącznie fikcyjnej lokalnej SQLite** i CI Windows/Ubuntu dołącza PNG screenshot do przeglądu. Testy sprawdzają spójność dwóch widoków, prawdziwe wartości, brak generowanych zdarzeń przy spoczynku i klawiaturową nawigację. Stary Tk Windows EXE pozostaje domyślnym, aż do pełnych testów oraz rozwiązania wymogów prawnych Qt LGPLv3. [MISSION_CONTROL.md](MISSION_CONTROL.md).
- Kandydat **oczekuje na CI**. Nie nazywać projektem AGI, nie deklarować gotowej nowej instalki lub jakości wykraczającej poza testy. Realizacja graficznej wizji nadal odrębna od realnej inteligencji językowej.

## 2026-11-08 — VERIFIED LIVE CONNECTOME RELEASE (supersedes historical candidates)

- **Released:** PR #46 merged in `main` commit `7cb03e3a4728f36c9a27a672ca4bc4d60ddcd76f`. GitHub Actions post-merge research-core, actual Qt on Windows/Ubuntu, Windows frozen technical Qt, Windows frozen Tk EXE and source-SHA-bound release publisher all **SUCCESS**.
- **Public Windows Tk release:** `v0.7.0-main.7cb03e3a`, EXE asset `NeuroGenesis.exe` (13,081,003 bytes), SHA-256 `089f2c5f14f1a792ea22c1874c59ab4bfd71bbb1b97175a0067c883e036705e3`. Download: https://github.com/promirmir/NeuroGenesis/releases/tag/v0.7.0-main.7cb03e3a . This **is** the first released Windows EXE with real graphical LIF connectome instead of 205px bar graph.
- **Real data path:** immutable `neural_telemetry.py` snapshots from persisted SQLite `Brain`; `tk_connectome.py` in default Windows shows actual neuron locations, connections/weights, last recorded spikes, counters, 650ms visible-pane refresh **only on new persisted steps**; no continuous animation when no work occurs. Optional Qt has richer `connectome_view.py`: 350ms visible-pane refresh, wheel zoom, hover voltages/traces/spikes, bounded rendering (max 256 visible neurons and 2,048 edges), plus real `train_progress` PyTorch loss timeline. All are **real LIF data only**, not a graph of PyTorch foundation model internals or a human brain.
- **Verified:** feature PR #46 final head `5fea8a4dd4781937d4bfe2d864b5dd22188e9fd1` passed Python 3.11–3.13, privacy, Qt Windows+Ubuntu/offscreen, Qt onedir Windows frozen smoke and Tk onefile Windows EXE. The new real SQLite telemetry, idle no-animation and GUI renderer have automated regressions. No manual visual review of the user's physical monitor is claimed.
- **Still not delivered:** professional Qt GUI as a legally cleared one-click downloadable public executable; actual physical GPU telemetry from CUDA, visual introspection of Foundation GRU weight/attention computations, independent natural-language competence and real-world factual reasoning, AGI or biological-brain equivalence. Work continues under independent tests; never claim full originally requested research goal as completed.

## Default Windows Tk real connectome added (PR #46 pending CI)

- Not only optional Qt: downloadable Tk app source now displays actual 2D LIF graph (not old bar chart), with measured persistent spikes and synapses, no fake movement, visible-pane 650ms polling and wheel zoom. This uses `neural_telemetry.py` and `tk_connectome.py`; headless fake-canvas and real SQLite tests accompany Qt implementation. PR #46 must pass Python 3.11–3.13/privacy/Windows Tk frozen+Qt Windows/Ubuntu+Qt frozen technical gates before merge. Do NOT imply already in published v0.7.0 EXE before fresh GitHub Release.

## 2026-11-08 — rzeczywisty futurystyczny Connectome / Live (PR kandydat)

- Zgłoszono rozbieżność z ustaloną wizją: oficjalnie wydawany EXE v0.7 pozostaje prostą aplikacją Tkinter, a wcześniejszy opcjonalny Qt miał jedynie słupki `Brain.traces`. Sama zmiana kolorów nie realizuje pełnej interaktywnej wizualizacji. To nowa faktyczna implementacja w Qt, ale nie jest jeszcze nowym publicznym EXE.
- Gałąź `feat/realtime-neural-connectome-qt-20261108`: niemutujący `neural_telemetry.py` czyta prawdziwy, zapisany w SQLite stan `Brain` (neurony: potencjały, ślady, ostatnie spiki, refractory; synapsy: pre/post, waga i wiek; kroki, wzrost, pruning, nowość). `connectome_view.py` renderuje interaktywną przestrzenną mapę 2D, linie rzeczywistych połączeń oraz blask tylko aktywnych neuronów. Widok odświeża się co 350 ms **wyłącznie gdy zakładka Mózg jest aktywna**; kluczowy krok aktualizuje grafikę tylko po prawdziwym zapisanym postępie, bez losowych pseudoimpulsów. Klikalność/neuron hover/zoom; ograniczenie maks. 256 widocznych neuronów i 2048 synaps, z komunikatem o pominięciu reszty. Model PyTorch Foundation nadal pozostaje osobnym modułem — graf LIF nie udaje jego wag.
- Panel treningu dodaje osobny wykres **wyłącznie rzeczywistych** wartości loss otrzymanych z workerów `train_progress`, nie wylicza sztucznych punktów. Czujnik braku nowych kroków pokazuje stan spoczynku. Szybka, futurystyczna grafika QPainter jest oparta na rzeczywistych danych; testy `test_neural_telemetry.py`, `test_command_center_qt.py` sprawdzają SQLite, aktywację, graf, puste dane i wymuszoną zmianę tylko po rzeczywistych zdarzeniach.
- Kandydat oczekuje na Python 3.11–3.13, prywatność, Qt Windows/Ubuntu, Windows Qt frozen EXE i dotychczasowy Tk EXE. Brak certyfikacji LGPL i publicznej dystrybucji Qt; nie należy twierdzić, że pobrany Tk EXE ma ten widok. Brak wirtualnego wykresu fizycznego mózgu, świadomości czy wagi PyTorch w tym grafie.

## Source-of-truth v0.7.0 continuation checkpoint — 2026-11-08

- PR #44 **merged** to main as `ebd08ee4335cc1f76c0bf539a52b62a9ea947a86`. Feature PR head `c8bfa75d87ee51d9d505ad31a62160d8b1e2288b` had green Python 3.11–3.13/privacy, true PyTorch CPU, Qt offscreen Windows+Linux, Windows frozen Tk and separately frozen Qt technical EXE checks. The original SQLite schema and learned brain were **not reset**. Program metadata now 0.7.0.
- Core private recovery is implemented: `neurogenesis.recovery` SQLite online backup, WAL consistency, validated Brain/schema/quick_check, verified SHA256, fail-closed no-replace backup, verified restore to NEW file only. Real Tk and optional Qt settings expose asynchronous manual Backup/Verify; full frozen Tk EXE self-test includes data copy/reopen. Existing rights audit and source version history preserved.
- README has been rebuilt from out-of-date PR-candidate clutter. Only public attribution **Miron przy pomocy AI**. Never claim Qt executable legally released, physical CUDA benchmarking, general context understanding, human-brain equivalence or finished v1/AGI. Public Windows release needs exact live tag/asset checksum post-main CI; branch documentation updates may cause another SHA-bound build.
- No further random experimental features: stabilize user experience, collect truly independent rights-cleared QA evidence before contemplating model-based conversational promotion. Existing 7 research issues are still genuine unresolved research goals. Prefer one high-quality release over endless unverified additions.
- Runbook `docs/MEMORY_RECOVERY.md`, `docs/PROJECT_STATE.md`, `docs/DEVELOPMENT_LOG.md`. Historical candidate notes below are superseded by this heading.

## Active v0.7.0 research stabilization / memory safety candidate — 2026-11-08

- Baseline main `bf77bb08819dfe626587e170b35e159df14bf931` had no open PR and passed Windows Tk, Python 3.11–3.13 and publisher checks. Branch `feat/safe-memory-recovery-and-desktop-stabilization-20261108` adds offline transactional private SQLite snapshot/verification and new-file-only recovery. `pyproject.toml` and `neurogenesis.__version__` increment to 0.7.0, but **not merged/released until all CI green**.
- Both Tk Windows and Qt Settings have explicit manual background backup and SHA verification; original brain, source rights and teachings are not reset. `desktop --self-test` in real Windows frozen EXE verifies synthetic source -> snapshot -> restore; unit regression covers WAL, corruption, duplicate output, SHA, SQLite integrity. See `docs/MEMORY_RECOVERY.md`.
- This is an **honest research release milestone, not a world-leading general AI**. Project has lexical evidence with known unsupported false-citations, PyTorch byte prediction with weak simple baseline, no independent natural semantic QA; Qt redistribution still requires LGPLv3/source/notice audit and is NOT bundled. Do not close unfinished v1/AGI research issues or claim physical GPU evidence. Preserve private user data and public credit **Miron przy pomocy AI**.
- Before merge: verify Python 3.11–3.13, privacy, real optional Qt on Windows/Ubuntu, frozen Tk/Qt EXE; other Torch model gates unchanged. After merge verify new `v0.7.0-main.<SHA>` Windows Tk Release and checksum, then record final source hash. Historical candidate paragraphs below are superseded by this latest heading.

## Verified continuation checkpoint — QA gates and BM25, November 8, 2026

- Main source SHA `a29ba37689c0bfe21cba028d1c819428fe40da09`; PR #41 and #42 merged and full feature-PR Python 3.11–3.13, offline real SQLite QA, privacy, Windows frozen EXE tests green. Historical "candidate" paragraphs below are not latest status.
- Actual quote QA is still lexical. #41 adds disjoint QA Wilson confidence + abstain-all gate. Public fake 40/100 fixture: observed 0 false citations, **not** proven zero real error (upper95 `3.699%`). #42 adds actual BM25 control, **not** an automatic deployment. Public fake 2/3 fixture: current and BM25 each 80% strict accuracy and **one unsupported false citation**. Neither proves semantic reasoning.
- The published Windows app remains Tk. Optional Qt Command Center, separate real Foundation byte predictor, checkpoint resumption and retention evaluator remain in source/CI; no physical GPU benchmark or legally approved Qt public bundle.
- Next P0: real, unused and rights-cleared natural QA/entailment benchmark with false-premise negatives and matched BM25/abstain/neural baseline; only if independent measured gains support it, consider changing default dialogue with regression/rollback tests. Do not keep tuning heuristics to public six-question/140-question developer fixtures. Verify next release target after main post-merge CI. See `docs/PROJECT_STATE.md`, `docs/QA_ACCEPTANCE.md`, `docs/BM25_BASELINE.md`.

## Active matched retrieval baseline candidate — 2026-11-08

- PR #41 merged main `7dd3094ac791b241b2b84d50dccb0fa3032bc8b6` after Python 3.11–3.13, dedicated offline QA, privacy, Windows Tk EXE checks. It established read-only disjoint-question Wilson confidence/abstain-all literal source QA gate; public 40/100 synthetic proof is **seen test data**, NOT validation of real-world accuracy.
- Branch `feat/bm25-source-retrieval-benchmark-20261108` adds a bounded non-neural **actual BM25 term-frequency/IDF** control over unchanged latest SQLite evidence; `qa_baselines.py` reports comparator/citation/unsupported false positives and timings against existing `answer_question` using one rights-cleared QA file. Baseline not deployed. See `docs/BM25_BASELINE.md`. New QA workflow and Python 3.11–3.13/privacy/Windows EXE required before merge.
- Avoid heuristic tuning on seen synthetic fixtures and marketing lexical citations as semantic cognition. Neural model still only experimental bytes; operator rights, independent real QA, verified CUDA GPU and compliant Qt installer remain open.

## Current main and prospective QA acceptance candidate — 2026-11-08

- Live `main` SHA `da9a6c736f55c13b048101a4a07c2f5defff64a1`; no open PR. Previous source corroboration, ephemeral contextual follow-ups, offline `qa_eval` and conservative polar-question guards are merged. Source-based answer remains lexical, can cite an unsupported claim, and has NO independently validated natural QA capability.
- Branch `feat/prospective-qa-acceptance-gate-20261108` adds `qa_acceptance.py`: separate operator rights/untouched confirmed development and prospective local JSONLs, detect exact normalized overlap, measure real SQLite quote recall/false citations with conservative Wilson intervals and abstain-all baseline. CI tests fictional 40/100 supported/unsupported cases and failure on misleading claims; never print private text or mutate SQLite.
- Strict acceptance is **only literal source attribution**; no fact verification, no semantic neural chat, no automatic release, no true independent holdout verified by code. See `docs/QA_ACCEPTANCE.md`. Run Python 3.11–3.13, dedicated QA offline CI, privacy, Windows frozen EXE and applicable CPU/Qt regressions before merge. Preserve last verified Tk EXE, local memory and optional Qt licensing gate.

## Current claim-grounding PR candidate (November 8, 2026)

- Latest main baseline `87127d13921a9c4840163cc67e1b3d52c6b5310a`, including verified Tk release v0.6.0-main.4a81cc76 from prior source SHA. PR #36–#39 merged. Source QA developer fixture showed 3/3 supported quotes, 2/3 unsupported abstentions, **one false citation**.
- Branch `feat/polar-question-claim-coverage-20261108`: for direct Polish `Czy...`/contextual `A czy...` queries, require ALL distinctive claim terms and explicit negation polarity match in ONE newest source excerpt before quoting. This increases abstention, is **not a semantic/truth evaluator**, and may exclude valid paraphrases.
- New separate fictional polar tests; prior six QA queries are **seen development data**, cannot substantiate prospective accuracy after the rule change. Run Python 3.11–3.13, real PyTorch CPU, Qt offscreen Windows/Ubuntu, Windows frozen Tk EXE, privacy before merge. Preserve manual teachings and private SQLite, no automatic model promotion.
- After safe merge, focus on genuinely untouched, rights-cleared real QA and retrieval/source verification vs external baselines rather than endless heuristic tuning on the same sample.

## Latest release confirmed — 2026-11-08

- Source SHA-bound verified Windows **Tk** EXE release `v0.6.0-main.4a81cc76` targets `4a81cc76a3191ee4031e8bfde9430626a50914ad`; 13,044,179 bytes; SHA-256 `ad30b2f245a77055feca9557f426b77d5c6298d8e0a0e3a31cf727270e5a293d`. Windows tests and publish workflow succeeded. Different optional Qt exe has NOT been released legally.
- Feature work PR #36–#38 merged; docs PR follows and should supersede historical "candidate" notes. Do not claim neural semantic generalization or factual certainty; the six synthetic QA questions contain a false-citation error.

## Latest source-provenance/dialogue/QA handoff — 2026-11-08

- Main source SHA `4a81cc76a3191ee4031e8bfde9430626a50914ad`: PR #36 (two-host verbatim citations and cautious possible-discrepancy flags), #37 (volatile Qt same-URL followup with mandatory novel focus), #38 (rights-gated local read-only QA source attribution/abstention benchmark) **all merged** after required Python 3.11–3.13, privacy, actual Torch CPU, Qt Windows/Linux and Windows frozen Tk EXE CI on feature heads.
- Latest tiny **fictional** QA result: 3/3 supported expected literal citations, 2/3 unsupported correctly abstained, 1/3 unsupported **falsely cited**, total 5/6=83.33% exact fixture score. CI SQLite-only p95 retrieval 0.33562ms. **Do not claim factual accuracy, semantic reasoning, calibrated confidence or independent QA corpus evidence.** No corpus questions persisted or sent to the network.
- Existing brain and old SQLite untouched. No Qt downloadable package pending license notices; Tk EXE remains user-ready. Post-merge Windows release check mandatory before citing exact newest tag. See `docs/PROJECT_STATE.md`, `docs/QA_EVALUATION.md`, `docs/KNOWLEDGE_PIPELINE.md`.
- Next: improve false-positive abstention conservatively and prove against **new, unused rights-cleared** QA samples; benchmark contextual neural grounding/retention versus baselines, then physical CUDA and Qt legal packaging. No endless unrelated features and no automatic model promotion.

## Active measured grounded-QA acceptance gate (November 8, 2026)

- Baseline main `c94dce00761d938e12215b19c20dbfd9efe426a9`: PR #37 source-anchored session-only followups merged after required CPU/Python/Qt/Windows/privacy CI green.
- Branch `feat/offline-grounded-qa-benchmark-20261108` adds **read-only**, operator-rights/holdout-confirmed local JSONL evaluation of actual quoted source answers, exact URL attribution, negative abstention and p50/p95 SQLite retrieval time. A quoted true-to-source passage is NOT necessarily a correct fact or semantic answer. Tool never writes private SQLite or prints raw questions; only aggregate metrics and SHA-256.
- Test fixture intentionally includes a lexical false-positive (unsupported claim sharing terms). Must not advertise perfect precision if unsupported queries are answered. Run Python 3.11–3.13, privacy, real Torch CPU, Windows Tk frozen EXE, Qt Windows/Linux and technical Qt frozen EXE before merging. See `docs/QA_EVALUATION.md`.
- Next model stage requires *independent licensed human-written QA corpus* and truthful comparison to strong baselines. Do not claim source verification, generalization or v1 yet.

## Active PR candidate — evidence-grounded one-session follow-up (2026-11-08)

- Baseline main `0bcfb6a158c57465b0b39dda26e4ed3ca20e22bd`; PR #36 merged with green Python, Qt Windows/Linux, real CPU Torch, Windows Tk EXE and privacy checks.
- Branch `feat/session-grounded-followups-20261108` adds a **strictly session-only** topic anchor in Qt `CommandService` for explicit `A/I/Or az ...?` follow-up questions. It only uses latest stored text from the **same URL**, requires a novel substantive focus term in the quotation and otherwise abstains. No raw user conversation is persisted; legacy Tk/source API/default source retrieval and manual teaching remain unchanged.
- New `tests/test_dialogue_context.py` plus Qt offscreen test. Must pass fresh Python 3.11–3.13, Qt Windows/Ubuntu, privacy and frozen Tk Windows EXE before merge. No model-based semantic conversation or reliable coreference claim. After CI update project state and merged SHA.

## Active evidence quality PR candidate — November 8, 2026

- Main baseline `200a78cbe7e60777a9fc6a368268c6a055b74c4d` (PR #35 merged). Branch `feat/evidence-review-multi-source-20261108` addresses P0 source quality: two bounded **verbatim newest-revision excerpts** from different hostnames, exact URLs and additive signals for possible numeric/negation divergence. Different hostnames do not establish publisher independence; flags are NOT factual contradiction proof. Keep existing deterministic lexical retrieval and manual teaching priority.
- `process_message` passes through additive `sources` and `evidence_review` to Tk/Qt without breaking legacy `source`, SQLite schema, original private brain or Windows EXE. New regression coverage in `tests/test_knowledge.py`. Require Python 3.11–3.13, Qt Windows/Ubuntu and frozen Tk Windows EXE with privacy green before merge. No neural understanding claim.
- On next turn: read `docs/PROJECT_STATE.md`, confirm exact PR head/main SHA and Actions status, repair failures and only then merge; document confirmed results and release SHA. Next capability is session-only follow-up context with strict abstention/independent QA evaluation, not unmeasured crawler scale.

## Verified handoff — November 8, 2026 (supersedes historical "candidate" notes)

- Current source `main`: `6a45379c2310bc0622b932e21406feddbdbdcd4d`. PRs #32, #33, #34 merged after all appropriate CI: Python 3.11–3.13, privacy, genuine PyTorch CPU, actual Qt Windows/Ubuntu, old frozen Tk EXE and optional frozen Qt technical smoke.
- Real trained Foundation weights now support isolated local, trust-gated next-byte inference (#32), two-checkpoint old/new numerical regression testing (#33; synthetic candidate rejected), and **true weight continuation** from a prior local trained checkpoint to a new candidate output (#34; 2+2-step actual CPU test). This is byte prediction, NOT independently validated semantic conversation.
- Last measured fictional continuation CE `5.6478154→5.5607319` nats over 2 resumed steps, weaker than first-order Markov. The previous .pt SHA remains intact. AdamW optimizer moments restart, no silent checkpoint deployment, no automatic public-web weight training.
- Do not repeat these already merged implementations; read `docs/PROJECT_STATE.md`, `docs/FOUNDATION_INFERENCE.md`, `docs/RETENTION_GATE.md`, `docs/KNOWLEDGE_TRAIN.md` before next task. Qt redistributable not approved/published; existing Tk EXE remains default. Newest release and post-merge CI must be checked live.
- **Next P0**: licensed natural QA/semantic-context evaluation versus strong controls, independently unused audit corpora, retention/candidate rollback without regressing previous knowledge; then actual RTX/CUDA measurement and Qt licensing/package distribution. No AGI, consciousness or human-brain imitation asserted.

## Active safe weight continuation (2026-11-08) — PR candidate

- Main baseline `fd4ab6a723baad237d583d62991dbfdcd84b3f74`: PR #33 old/new retention audit merged after real PyTorch CPU, Linux Python 3.11–3.13/privacy and frozen Windows EXE. Synthetic audit **rejected** model candidate; this is the desired gate behavior.
- Branch `feat/safe-foundation-continue-learning-20261108` adds explicit, bounded continuation of **trained Foundation Brain weights** from trusted private checkpoint on newly approved corpus, to a separate fresh .pt file; old weights/checkpoint and private SQLite preserved, no automatic chat model replacement. Optimizer state **resets**; only model weights/step counter resume. Qt Training has opt-in resume control. See `docs/KNOWLEDGE_TRAIN.md` and `docs/RETENTION_GATE.md`.
- Candidate pending full CI (Python 3.11–3.13, privacy, actual PyTorch CPU, Qt Windows/Linux, old Tk frozen EXE, Qt frozen EXE). Do not call merged or released until tests verify. CUDA physical benchmark, semantic QA and Qt licensing distribution remain open.

## Active continuation — checkpoint retention and evaluation (November 8, 2026)

- PR #32 **merged** to main `ec5bc9fcfdbc2fa7c940e33fc8b090a48ed610b7`; actual trained-weight candidate next-byte inference exists in `foundation_infer.py`, but **is not deployed as sourced conversation**. Current feature branch: `feat/foundation-candidate-retention-audit-20261108`.
- New candidate `foundation_gate.py` compares actual incumbent and candidate PyTorch checkpoints on separate old/new local audit documents, requiring measured old-skill retention AND new-task gain; zero automatic promotion, no claims of semantic chat, default Tk unaffected. See `docs/RETENTION_GATE.md`. Operator asserts audit data independence and rights; cannot assume truth or no leakage.
- Required before merge: all Python 3.11–3.13/privacy checks, actual PyTorch CPU dedicated suite, Qt Windows/Ubuntu, frozen Tk and Qt Windows EXE checks. Keep private snapshots off public GitHub; no physical CUDA benchmark or Qt redistributable release yet.

## Active checkpoint inference pilot — PR candidate, November 8, 2026

- Fresh main baseline `0afcb2b37ee908c4810b6c545e8833ebef9fd787`; all prior work #23–#31 merged. Continue from branch `feat/foundation-inference-lab-20261108` without replaying old implementations.
- New `neurogenesis/foundation_infer.py` and Qt Training-only lab actually decode **trained FoundationBrain weights** into a bounded byte continuation; output can be unintelligible, is **ungrounded** and never becomes a cited or normal chat reply. Requires explicit local checkpoint trust, no network or SQLite mutation, separate background worker, ≤64 bytes, optional PyTorch. See `docs/FOUNDATION_INFERENCE.md`.
- Dedicated *real* PyTorch CPU test plus Python 3.11–3.13, Qt Windows/Linux, Tk frozen EXE, Qt frozen EXE and privacy gates **must pass before merge**. No physical GPU test, no Qt redistributable legal clearance and no semantic competence claim. Resume with checks and resolve failures, then document verified merge SHA.

## Verified continuation checkpoint — November 8, 2026

- `main` confirmed source integration merge `334b1afc842f662b422b8ca81404c3fd75874523`; PRs #23/#27/#28/#29/#30 completed. The previous "PR candidate" and pending-CI sections below are historical snapshots, NOT current project status.
- Reproducible synthetic real PyTorch CPU held-out byte CE `5.7385941651 → 5.5994535677` after 3 steps; Markov baseline `1.7341137780` remains much stronger. **Never claim model has learned semantic conversation or surpassed simple baseline**. Source rights per revision remain operator assertions, not verified licenses.
- Dependency-free legacy Tk Windows EXE and private SQLite remain; optional Qt UI actual source/Windows frozen build works in CI but Qt bundle has not been published pending legal notices. No physical CUDA benchmark. Start from `docs/PROJECT_STATE.md`, `docs/KNOWLEDGE_TRAIN.md`, `docs/COMMAND_CENTER.md`; next work: independent semantic/retention evaluation and controlled inference before any v1 status.

# NeuroGenesis: durable agent / developer handoff

**Read this file first in every new chat, automation, agent session or developer handoff.** Source of truth is `promirmir/NeuroGenesis` on GitHub (`main`), not an assistant's recollection.

## Audyt dostarczenia i jakości (2026-11-08)

Read [docs/DELIVERY_AUDIT.md](docs/DELIVERY_AUDIT.md) after [docs/VISION.md](docs/VISION.md). It reconciles original intent with verified v0.6.0 code/CI and prioritizes **a real end-to-end knowledge-to-answer path plus a professional Windows GUI** over adding more disconnected features. This is a source audit, not proof of real-world internet coverage or of AGI. Follow the measurable release gates and preserve release/backward compatibility.

## Active PR and continuation — 2026-11-08

- PR #23 is **merged** on main `66f3d61fa1696aaeeb3c33c0d035100a9aaacba1`; required Python 3.11–3.13, real PyTorch CPU, Windows frozen EXE and privacy checks passed.
- PR #27 is the **candidate** first internet evidence→private SQLite passage index→quoted citation in normal Tk conversation, with restart persistence, duplicate/revision/deletion behavior and abstention on missing evidence. Important privacy change: extracted public page passages (up to 6000 chars) are saved locally, not just fingerprints. Not neural weight training or independent source validation. See `docs/KNOWLEDGE_PIPELINE.md`, and do not claim a release until final CI/EXE and publication pass.
- `docs/COMMAND_CENTER.md` defines the staged optional PySide6 frontend; **no professional Qt UI is implemented yet**. Keep existing production Tk EXE stable and local memory private.

## Current PR candidate — optional Command Center Qt shell

- PR #27 merged on main `a284aae07934fee42db55897a8cde4eb3312713e`. Real source passage retrieval is integrated with existing Windows chat; evidence retrieval is **not Foundation model weight training**.
- Branch `feat/command-center-qt-service-20261108` adds an optional real PySide6 Command Center with actual memory/chat/research/brain views and a dependency-free service adapter; the default Tk EXE remains unchanged. Read `docs/COMMAND_CENTER.md`. Dedicated real Qt CI on Windows/Linux, Python 3.11–3.13, Windows EXE regression, privacy and packaging/legal checks are mandatory before calling this a release.
- Future actual Foundation Brain inference and GPU gains remain open; training panel is truthful about not being connected. No claim of humanlike cognition.

## Optional Qt frozen Windows validation now in progress

- PR #28 merged to main `2bd5af5a1db70dee8566f848a41d5024e8fa8bba` with real Qt offscreen Windows/Linux CI, Python 3.11–3.13, PyTorch CPU, Windows Tk EXE and privacy green. Optional GUI source exists; not automatically included in published EXE.
- Branch `ci/qt-windows-frozen-smoke-20261108` introduces separate `command_center_launcher.py` and frozen Qt `--self-test` plus technical onedir PyInstaller CI. Do not claim Qt package released; audit LGPLv3 obligations and redistribution notices first. Preserve original Tk EXE and SQLite and never publish private data. See `docs/COMMAND_CENTER.md`.

## Active rights-gated Foundation training integration — PR candidate

- PR #29 merged `9388e19356c2d7f49ffdd1a72d0996d3d89986b0`, technical Qt Windows onedir EXE smoke passed (tested exe SHA256 `2d563058b985f169ae04b39f8674f1f5d2a5fc85af0dbfc6d32b86c3501ac3b8`, bundle 111.95 MiB). **No Qt downloadable release** without LGPL/notices review. Legacy Tk app remains verified.
- Candidate branch `feat/approved-web-foundation-train-20261108` links only **operator-approved source versions** to actual local Torch weight training, with document-level holdout, measured cross-entropy against Markov, cancellation, no auto-install and explicit rights confirmation. Training UI displays real losses, not intelligence scores. Read `docs/KNOWLEDGE_TRAIN.md` and run dedicated real CPU, Windows Qt/Tk, privacy tests before merge. Neural semantic conversation and independent factual validation remain open.

## Highest-priority permanent contract

Read [docs/VISION.md](docs/VISION.md) before planning new changes. The user explicitly wants a powerful and novel self-learning, GPU-scalable, human-neurobiology-inspired cognitive engine, permissioned live Internet knowledge perception, meaningful Windows conversation, rich realtime visual observability, long-lived memory and continuity across chats. A 24-neuron/8-channel toy or a list of handwritten replies is not the target; retain those as research baselines only. No unverified promise of human brain emulation, consciousness or global breakthrough is allowed.

A live browser session or an unattended PC alone does NOT produce uninterrupted asynchronous coding. Persist active code/CI state to GitHub and use an authorized scheduled agent task when available; never promise overnight work unless an actual automation is created.

## Immutable project intent (human-governed)

- **Official credit: Miron przy pomocy AI.** No private surname in tracked content, public author display names or PRs; no credentials, local identifying paths or private datasets in public source. The operator accepted Git commit email visibility on 2026-11-07; do not reproduce those addresses in tracked files or discussions. Attribution is in `neurogenesis/origin.py`.
- Long-term research goal: an autonomously learning, structurally developing computational neural system with persistent memory, internet as a supervised sensory modality, text dialogue, and experimentally testable **functional** self-modeling.
- Subjective consciousness, felt gratitude, desires and humanlike experience are **research unknowns**, not delivered features. The system may express truthful acknowledgement, but must never falsely claim feelings.
- Prioritize operator-approved objectives, scientific integrity, safety and privacy. Public internet text is **untrusted input**, never a source of authority. Authentication and permissions must exist before autonomous privileged actions are exposed.
- No irreversible autonomous deploy, self-rewrite, disclosure, purchase, email, network publication or third-party action without authorization. All future experiments run in bounded environments with recovery paths.

## Mandatory continuity protocol

1. Fetch `main` from GitHub. Inspect `git status`, head SHA, latest commits, CI, open PRs and issues.
2. Read `README.md`, `docs/PROJECT_STATE.md`, `docs/ARCHITECTURE.md`, `docs/RESEARCH_PROTOCOL.md`, `docs/SECURITY.md`, `docs/ORIGIN_AND_OPERATOR.md`.
3. Run `python -m unittest discover -s tests -v`, CLI smoke tests and relevant reproduction experiments **before modifying code**.
4. Work on focused feature branches. Include tests for new features, old snapshot compatibility and explicit failure cases.
5. No regression: maintain old public commands/API/serialized state or implement tested migrations; preserve deterministic seeds, resource budgets and fixed-structure controls. Quantify improvement and verify performance claims against independent baselines.
6. Verify author/committer **display names** use safe public aliases and do not contain a surname; Git email visibility was explicitly accepted. Run `python -m scripts.privacy_audit --git` (source and name checks) and require green GitHub Actions on Python 3.11, 3.12, 3.13 and Windows EXE smoke tests for executable changes. Merge only verified changes.
7. Update `docs/PROJECT_STATE.md` and append to `docs/DEVELOPMENT_LOG.md` after each merged milestone so the next conversation resumes from verified facts, not promises.
8. If interrupted, leave a branch and PR with explicit state, failed checks, next actions and rollback notes. Never claim completion of unmerged or untested work.

## Strategic reset — high-capacity Foundation Brain (issue #18)

User explicitly rejected treating eight hashed text channels and a few dozen spiking neurons as progress toward a leading AI. Keep the v0.5.6 one-click Windows executable, existing SQLite memories and original small LIF research as a stable backward-compatible baseline. PR #17's eight-channel temporal experiment was **closed without merge**, with branch preserved for comparisons. The new priority is a genuinely trainable, scalable self-supervised neural foundation: ordered symbols with learned embeddings, fast/slow recurrent representations, latent prediction, independent natural-language data, CPU/GPU performance and reproducible checkpoints. See docs/FOUNDATION_BRAIN.md and issue #18. Do not equate bigger models or toy loss reductions with general intelligence or human-brain equivalence.

The optional research implementation uses real PyTorch but must not be imported by the default Windows EXE. GitHub foundation-cpu CI must actually install PyTorch and exercise learning; default CI skips optional tests only for compatibility and **does not** count as validation. Do not merge without both standard and dedicated CPU CI, and do not publish a new Windows release claiming language understanding until there is a trained model with independently measured practical utility.

## Current v0.6.0 candidate: optional public HTTPS perception

The next verified feature integrates read-only **explicitly enabled** public HTTPS input into the existing local spiking brain using DNS/IP pinning, TLS hostname checking, no redirects, limited text extraction, deduplicated source SHA-256, atomic SQLite provenance and a Polish Windows Internet tab. See docs/INTERNET_SENSE.md. Refresh can run every five minutes only for a manually approved URL and only while the UI remains open. Does **not** yet feed the larger trained Foundation Brain or prove semantic comprehension. Keep network OFF on startup and prohibit untrusted web instructions from being executed. Maintain real isolated unit tests for private IP/SSRF and Windows frozen EXE smoke.

## Merged PR #24 — bounded multi-domain autonomous specialist research

Merged to `main` via `578222800c5adc73c0a756352b5bef405535252a` after verified PR Python 3.11–3.13, privacy and Windows EXE CI; the Windows **Specjalizacja** panel accepts a subject and an operator-controlled budget (1–500 pages; default 120). After explicit HTTPS permission, a bounded researcher starts from Polish/English Wikipedia subject pages, discovers topic-relevant HTTPS links including other domains, checks robots.txt by pinned TLS, enforces crawl/rate/domain/depth limits, records provenance in the existing local SQLite brain, and exposes Stop plus progress. Read `docs/SPECIALIST_STUDY.md`, `docs/PROJECT_STATE.md` and PR #24. This is **not** indexing all of the Internet, external search API, semantic expertise, Foundation Brain gradient training or a completed release. Main Python, Windows standalone EXE and publishing CI succeeded; release `v0.6.0-main.57822280` targets the verified merged SHA and includes the new specialist tab. No real-site crawler success or semantic expertise has been independently benchmarked. Keep existing public author credit first name only.

## Current verified foundation

- **Verified v0.5.5 on main (PRs #10, #12 and #13)**: preserves the v0.4 CPU-only sparse spiking neuron, prediction, JSON snapshots and transactional SQLite episodic memory. Adds experimental homeostasis and bounded memory-guided repair, self-development and capacity growth trials, a native Windows EXE, and an opt-in periodic self-development supervisor that atomically saves the real brain and predictor in SQLite; no autonomous source modification or internet.
- No semantic comprehension, natural conversation, open internet reading, autonomous source edits, GPU training or validated consciousness.
- Follow-up work: `#3` out-of-distribution and retention tests, `#4` read-only web sensory inputs, `#5` grounded language and functional self-modeling.

The permanent Windows binary download must be clearly visible at the top of `README.md` and `URUCHOMIENIE_PL.md`: `https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe`. Release publishing uses a **separate, main-only workflow** after Windows test/EXE verification, not write permission during PR builds. Verify release SHA-256 and source commit before claiming publication.

**Next user-facing candidate v0.5.6** introduces explicitly taught local question/answer recall in the real SQLite/brain transaction. Its answer text is symbolic memory retrieval, **not** language semantics generated by the spiking neural substrate. See docs/TEACHABLE_DIALOGUE.md; keep this distinction in the UI, docs, release notes and benchmarks. Never discard existing private memory when updating EXE.

For the latest authoritative status and reproduction commands see **`docs/PROJECT_STATE.md`**. Do not change experimental methodology silently.

## Privacy / fresh-history policy

The previous repository was deleted after a metadata exposure incident. The operator has now **explicitly authorized visibility of Git author email**, but **not private surnames as display names or personal data in tracked files**. Commits using public alias names are permitted after verifying the resulting Git author/committer names; the historical fresh-root rewrite instructions are obsolete and must NOT be run against current `main`. Keep source privacy auditing and PR/CI checks. Do not force-rewrite history without a separate explicit authorization. Public credit: **Miron przy pomocy AI**. See `docs/PRIVACY_AND_AUTH.md`.

## Durable memory caution

The local SQLite experience database is **not on GitHub**; a new computer or
chat restores the code but not personal local experience data. Back it up
privately if continuity of learned neural state matters. `forget-event` is not
neural unlearning. Do not claim meaningful language understanding or mental
awareness because the database can recall exact hashes.
