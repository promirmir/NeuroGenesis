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
