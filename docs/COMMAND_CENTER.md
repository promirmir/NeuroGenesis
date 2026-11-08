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
