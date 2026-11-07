# NeuroGenesis — Windows desktop EXE

**Direct Windows download:** [NeuroGenesis.exe — latest verified GitHub Release](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe) · [SHA-256](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256). This is the preferred public download; workflow artifacts are transient engineering diagnostics. Releases are published automatically only after a successful main Windows build and binary checksum verification.

A native Windows desktop application, not a command-line interface or a browser page.

## For users

Once a release has been tested and published, download `NeuroGenesis.exe` and double-click it. No separate Python installation is required. The current panel offers **Rozmowa** (sensory observations), **Mózg** (live neural-state measurements) and **Internet** (explicitly OFF until safe sensory access is implemented). It is not a natural-language reasoning assistant yet, and no claim of consciousness is made.

Private neural/episodic memory is stored separately in `%LOCALAPPDATA%\NeuroGenesis\experiences.sqlite3` (not inside the executable), so replacing the EXE does not delete the DB. Back up this private file before changing machines. Raw message text is **not stored by default**; hashed features and their hashes are not encryption. The application never contacts an internet server in this build. Quit with the window close button.

## Maintainer: build and verify on Windows

The Windows GitHub Actions workflow `.github/workflows/windows-exe.yml` builds the real Windows PE executable with PyInstaller. Before packaging it checks tracked source for sensitive data and author display-name safety using the current repository policy (issue #6 is closed; Git author email visibility is operator-approved).

The build runs the full regression suite and local SQLite smoke test, packages with `--onefile --windowed`, and verifies the frozen `NeuroGenesis.exe --self-test` before publishing a temporary Actions artifact. A **separate, privileged, default-branch-only** `.github/workflows/publish-release.yml` reacts to completed successful `main` builds, independently validates the SHA-256 and executable format and creates an immutable commit-specific GitHub Release with the EXE and checksum. Pull-request builds cannot publish releases.

Local Windows build (maintainers):

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
