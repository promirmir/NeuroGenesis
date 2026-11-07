# NeuroGenesis — Windows desktop EXE

A native Windows desktop application, not a command-line interface or a browser page.

## For users

Once a release has been tested and published, download `NeuroGenesis.exe` and double-click it. No separate Python installation is required. The current panel offers **Rozmowa** (sensory observations), **Mózg** (live neural-state measurements) and **Internet** (explicitly OFF until safe sensory access is implemented). It is not a natural-language reasoning assistant yet, and no claim of consciousness is made.

Private neural/episodic memory is stored separately in `%LOCALAPPDATA%\NeuroGenesis\experiences.sqlite3` (not inside the executable), so replacing the EXE does not delete the DB. Back up this private file before changing machines. Raw message text is **not stored by default**; hashed features and their hashes are not encryption. The application never contacts an internet server in this build. Quit with the window close button.

## Maintainer: build and verify on Windows

This repository includes a Windows GitHub Actions workflow `.github/workflows/windows-exe.yml`, intended to generate the real Windows PE executable on a Windows runner using PyInstaller. It fails before packaging if Git history exposes non-noreply commit identities. **Issue #6 blocks publication until the existing historical metadata is fixed.** Do not disable this gate to get a green build.

The workflow runs the existing regression suite plus the desktop's real SQLite smoke test, bundles with `--onefile --windowed`, and runs `NeuroGenesis.exe --self-test` before uploading the EXE as a short-lived GitHub Actions artifact. The workflow does not automatically create a public release or modify Git history. Manual publishing requires separate verified review.

Local Windows build (only after privacy remediation):

```powershell
py -3.12 -m pip install "pyinstaller>=6,<7"
py -3.12 -m unittest discover -s tests -v
py -3.12 desktop_launcher.py --self-test
py -3.12 -m PyInstaller --noconfirm --clean --onefile --windowed --name NeuroGenesis desktop_launcher.py
.\dist\NeuroGenesis.exe --self-test
```

Result: `dist\NeuroGenesis.exe`. GUI starts without extra flags; `--self-test` runs with no GUI and never reads/writes the user's real database.

## Engineering constraints

- Keep the old v0.4 `Brain`, `ExperienceMemory`, CLI and snapshot formats unchanged.
- A single EXE can update code without deleting the external SQLite brain state; never write mutable databases inside the frozen PyInstaller temporary extraction folder.
- No internet sensor or autogenous cognitive skills should be claimed until separately implemented and objectively validated.
- Always test builds on a real Windows runner. A Python source file is not itself a Windows EXE, and Linux packaging is not an equivalent Windows build.
- Public credit: Miron przy pomocy AI. No private personal metadata in commit authors or source files.
