"""Optional Qt Command Center EXE entrypoint, separate from stable Tk launcher.

The Windows Qt packaging workflow only runs a frozen self-test; it does not
publish a distributable Qt bundle before license and packaging review.
"""
from neurogenesis.command_center import main

if __name__ == "__main__":
    raise SystemExit(main())
