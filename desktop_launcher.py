"""PyInstaller-compatible native desktop entrypoint for Windows."""
from neurogenesis.desktop import main

if __name__ == "__main__":
    raise SystemExit(main())
