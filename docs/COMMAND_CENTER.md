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

## 2026-11-08 — rzeczywisty futurystyczny Connectome / Live (PR kandydat)

- Zgłoszono rozbieżność z ustaloną wizją: oficjalnie wydawany EXE v0.7 pozostaje prostą aplikacją Tkinter, a wcześniejszy opcjonalny Qt miał jedynie słupki `Brain.traces`. Sama zmiana kolorów nie realizuje pełnej interaktywnej wizualizacji. To nowa faktyczna implementacja w Qt, ale nie jest jeszcze nowym publicznym EXE.
- Gałąź `feat/realtime-neural-connectome-qt-20261108`: niemutujący `neural_telemetry.py` czyta prawdziwy, zapisany w SQLite stan `Brain` (neurony: potencjały, ślady, ostatnie spiki, refractory; synapsy: pre/post, waga i wiek; kroki, wzrost, pruning, nowość). `connectome_view.py` renderuje interaktywną przestrzenną mapę 2D, linie rzeczywistych połączeń oraz blask tylko aktywnych neuronów. Widok odświeża się co 350 ms **wyłącznie gdy zakładka Mózg jest aktywna**; kluczowy krok aktualizuje grafikę tylko po prawdziwym zapisanym postępie, bez losowych pseudoimpulsów. Klikalność/neuron hover/zoom; ograniczenie maks. 256 widocznych neuronów i 2048 synaps, z komunikatem o pominięciu reszty. Model PyTorch Foundation nadal pozostaje osobnym modułem — graf LIF nie udaje jego wag.
- Panel treningu dodaje osobny wykres **wyłącznie rzeczywistych** wartości loss otrzymanych z workerów `train_progress`, nie wylicza sztucznych punktów. Czujnik braku nowych kroków pokazuje stan spoczynku. Szybka, futurystyczna grafika QPainter jest oparta na rzeczywistych danych; testy `test_neural_telemetry.py`, `test_command_center_qt.py` sprawdzają SQLite, aktywację, graf, puste dane i wymuszoną zmianę tylko po rzeczywistych zdarzeniach.
- Kandydat oczekuje na Python 3.11–3.13, prywatność, Qt Windows/Ubuntu, Windows Qt frozen EXE i dotychczasowy Tk EXE. Brak certyfikacji LGPL i publicznej dystrybucji Qt; nie należy twierdzić, że pobrany Tk EXE ma ten widok. Brak wirtualnego wykresu fizycznego mózgu, świadomości czy wagi PyTorch w tym grafie.

## Verified status after source PR #44

Qt backup / verify Settings controls are implemented and actual Qt widget tests passed on Windows and Ubuntu. Frozen Windows Qt onedir technical self-test also passed, but **Qt redistribution is NOT authorized/certified**, and the public onefile EXE remains the Tk desktop. The project still lacks full LGPLv3 source/notice/relinking review and independent manual DPI review. `docs/MEMORY_RECOVERY.md` defines the shared transactional private backup contract. Source integration commit: `ebd08ee4335cc1f76c0bf539a52b62a9ea947a86`.

## Current v0.7.0 Command Center status (2026-11-08, release candidate)

The earlier "first candidate" wording below is historical. The optional real PySide6 Command Center has seven working views: source-cited conversation with volatile short topic follow-ups, bounded opt-in research, actual legacy brain traces, source version browser and consent, separately authorized real PyTorch byte-prediction training/inference, and settings. This branch adds a **nonblocking Settings → Backup/Verify** panel using the same private transactional SQLite snapshots as the Tk desktop. The tests verify the actual Qt view and job event queue; **no Qt EXE has been publicly released**.

**Qt licensing:** Official Qt states LGPLv3 distribution requires prominent notices, LGPL license copies, library source distribution or a compliant written offer, and the user's ability to replace/relink the covered libraries. A one-directory technical PyInstaller smoke test with replaceable Qt DLLs is not sufficient by itself. Do not distribute a Qt bundle until all applicable Qt/PySide6/Shiboken/third-party license obligations have been independently checked. Official references: https://www.qt.io/development/open-source-lgpl-obligations and https://www.qt.io/faq/qt-open-source-licensing . See `docs/MEMORY_RECOVERY.md` for data protection.

# NeuroGenesis Command Center — first functional Qt implementation (PR candidate)

**Public credit: Miron przy pomocy AI.**

## Delivered in this candidate branch (not yet a published Windows EXE)

- `neurogenesis/command_service.py` is a dependency-free Qt-independent adapter to actual `ExperienceMemory`, `process_message`, versioned web evidence, real `Brain.traces` and existing `SpecialistStudy` worker.
- `neurogenesis/command_center.py` is an **actual PySide6 application**, not a static UI mockup. It has a dark, scalable desktop navigation layout with seven functional views: Przegląd, Rozmowa, Badanie, Mózg, Trening, Wiedza and Ustawienia.
- Conversations reuse the **same existing SQLite brain and knowledge**. User-taught associations and source quotes have distinct provenance. Web passages are displayed as inert plain text. New source version selection and refusal on unsupported questions remain unchanged.
- Research Lab starts the existing bounded public HTTPS crawler only with operator-selected, session-scoped consent; worker is a daemon Python thread, SQLite uses per-call transactions and Qt UI polls a bounded event queue. Progress, Stop, error/source logs come from actual study events. Revoking consent stops the worker and blocks a later result from persistence. There is no auto-network startup.
- Brain Monitor paints only true `Brain.traces`. Training & Hardware honestly reports the Foundation model worker *not running*, and CUDA/VRAM not measured. No fake intelligence meter or decorative neuron activation.
- Sources view shows real URL/version/SHA-256 and retained plain-text excerpts. Dashboard shows actual memory, neurons/synapses and research status. Permissions & diagnostics show active permission and local DB path.
- Existing Windows Tk EXE and its launcher are **unchanged**. No Qt import is required by default or in the headless core. Optional dependency: `PySide6-Essentials>=6.8,<7`.

## How to run (optional research preview, not signed or released)

```powershell
py -3.12 -m pip install -e ".[command-center]"
py -3.12 -m neurogenesis.command_center
```

To use a specific existing private SQLite memory file:

```powershell
py -3.12 -m neurogenesis.command_center --db "C:\\path\\to\\private.sqlite3"
```

The default path follows the original Windows desktop `%LOCALAPPDATA%\\NeuroGenesis\\experiences.sqlite3`. Do **not** commit that database to public Git. Web text passages are stored locally in plaintext after opt-in web reads.

## Verification

- Dependency-free `tests/test_command_service.py`: real SQLite, restart, cited answers, neural state, no network default, revocable consent, fake in-process bounded research and manual teachings.
- Actual Qt widgets `tests/test_command_center_qt.py` with `QT_QPA_PLATFORM=offscreen`: seven panels, chat citation, source preview, session-scoped permission, no model mock responses.
- `.github/workflows/qt-command-center.yml` installs **real PySide6-Essentials** on both Ubuntu and Windows, checks QtWidget import, runs offscreen Qt tests and service/regression tests.
- Existing Python 3.11–3.13 and Windows Tk onefile build remain independent quality gates. CI cannot substitute for manual high-DPI visual/usability testing on hardware.

## Release and Qt licensing gate

This **optional source GUI is not yet the production default EXE**. Before redistributing Qt in a new EXE bundle, confirm the exact Qt LGPLv3/GPLv3/commercial license terms, bundled modules, permitted dynamic linking/relinking, notices, source access and packaging behavior. Qt for Python community license and dependencies: https://doc.qt.io/qtforpython-6/commercial/index.html ; Qt obligations: https://www.qt.io/development/open-source-lgpl-obligations ; Qt deployment tool: https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-deploy.html .

No automatic publishing of a Qt executable from this candidate until Windows packaging and license audit pass. The current standalone Tk EXE continues to ship and preserve private memory.

## Open work (do not misrepresent)

- Connect a separately approved actual Foundation Brain train/eval/inference worker, checkpointing, telemetry and prospective held-out questions; quantify CPU/CUDA and catastrophic forgetting. No PyTorch engine is active in Command Center now.
- Source quality/reliability, contradiction detection, license metadata, source backups/export and robust full-text ranking are incomplete.
- Research Pause/Resume requires a genuinely checkpointed queue and safe cancellation, so this preview exposes only Start/Stop; no fake pause.
- Windows Qt package size, high-DPI manual screenshots and redistributable legal notices must be verified before promotion to production.

## Technical Windows frozen-EXE verification candidate — PR #29

- New `command_center_launcher.py` is a **separate** PySide6 entrypoint. `python command_center_launcher.py --self-test` creates a temporary SQLite, ingests a synthetic web observation, reopens the database, performs a source-cited Qt chat and checks source browsing with HTTPS OFF. It does not touch private user memory or send network requests.
- `.github/workflows/qt-windows-frozen.yml` on Windows installs real PySide6-Essentials and PyInstaller, builds `--onedir --windowed` `NeuroGenesisCommandCenter.exe`, runs the **frozen** self-test, checks dynamically linked Qt6Core/Qt6Widgets DLLs and prints the exact EXE SHA-256 and directory MiB size.
- This is **only a technical packaging smoke**. No upload or GitHub Release: obligations under Qt LGPLv3 and other bundled libraries, third-party notices, replacement of DLLs, signing/update process and manual DPI/accessibility review are not yet certified. The old independently tested Tk EXE still releases normally.
- All claims depend on new CI results; a workflow file is not evidence of a passing build.

## Subsequent foundation-training integration candidate (PR after #29)

The Qt source browser now includes an explicit per-source-revision training rights approval/revocation dialog. Its Training panel offers an opt-in, bounded, cancellable real `FoundationBrain` PyTorch worker, CPU/CUDA device selection, per-step actual loss, whole-document held-out before/after cross-entropy and Markov baseline, actual training steps/s, and CUDA peak allocated bytes only when measured on hardware. It writes a separate numerical checkpoint **candidate**, never installs the model in chat automatically. The optional `[foundation]` dependency must be installed separately. Rights approvals do not establish factual truth or independent copyright verification. See `docs/KNOWLEDGE_TRAIN.md`; code and GUI candidates require full CI before merge, and Qt redistributable remains withheld for licensing review.

## Optional next lab — trained-checkpoint inference (PR candidate)

The Qt Training panel now proposes a **separate actual-weight inference** experiment, never automatically loaded or used for regular chat. The operator chooses a *trusted local checkpoint*, confirms provenance, enters a text prefix, and requests at most 64 deterministic predicted next-byte outputs, with real measured throughput and raw hexadecimal representation. The Qt controller dispatches all PyTorch work away from the UI thread and supports explicit stop. This is not semantic answering, evidence grounding or model deployment. See `docs/FOUNDATION_INFERENCE.md`; merge contingent on fresh real PyTorch and Windows/Qt gates, and no Qt redistributable is published by this change.

## Optional continuation control (PR candidate)

Qt Training has a disabled-by-default `Kontynuuj wagami` checkbox. When selected, the operator chooses the previous local `.pt/.pth` with the existing file picker, separately confirms trust and current source-corpus rights, and triggers a CPU/CUDA worker to load real weights and run bounded additional training steps. It produces an independent candidate filename, reports cumulative steps and explicitly notes that AdamW optimizer state starts fresh. No checkpoint is installed into chat or overwrites existing files. Implemented only as candidate until offscreen Qt Windows/Linux, real PyTorch CPU and both Windows frozen EXE regressions succeed.
