"""Fail-closed local privacy checks for public NeuroGenesis distributions.

This tool deliberately reports only file paths and finding categories, never
actual discovered values. It is heuristic and does not guarantee that data was
never exposed elsewhere (GitHub's PR/cache/ref history, forks, etc.).
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CHECK_EXTENSIONS = {".py", ".md", ".toml", ".yaml", ".yml", ".ps1", ".cmd", ".txt", ".json"}
CHECK_SPECIAL = {".gitignore", ".gitattributes"}
IGNORED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", "dist", "build"}

EMAIL = re.compile(r"\b[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}\b", re.I)
SECRET = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|(?:ghp_|gho_|ghu_|github_pat_)[A-Za-z0-9_]{8,}")
USER_PATH = re.compile(r"(?i)(?:[a-z]:[\\/]Users[\\/][a-z0-9._\-]+|/home/[a-z0-9._\-]+/)")
PHONE_WITH_PREFIX = re.compile(r"\+48[\s.\-]?(?:\d[\s.\-]?){9}\b")
# Avoid persisting private family names even as forbidden literals.
FULL_CREDIT_NAME = re.compile(r"\bMiron\s+[A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]{2,}\b")


def text_findings(content: str) -> list[str]:
    """Classify likely privacy issues without returning their sensitive values."""
    issues: list[str] = []
    for match in EMAIL.finditer(content):
        if not (match.group().lower().endswith("@users.noreply.github.com") or
                match.group().lower() == "noreply@github.com"):
            if "private email address" not in issues:
                issues.append("private email address")
    if FULL_CREDIT_NAME.search(content):
        issues.append("private family name following project initiator given name")
    if SECRET.search(content):
        issues.append("potential credential")
    if USER_PATH.search(content):
        issues.append("local user profile path")
    if PHONE_WITH_PREFIX.search(content):
        issues.append("phone number pattern")
    return issues


def source_findings(root: Path = ROOT) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in IGNORED_DIRS for part in path.relative_to(root).parts):
            continue
        if path.suffix.lower() not in CHECK_EXTENSIONS and path.name not in CHECK_SPECIAL:
            # Unrecognized binary files must not be accidentally committed.
            issues.append((str(path.relative_to(root)), "unreviewed file type"))
            continue
        data = path.read_bytes()
        if len(data) > 2_000_000 or b"\0" in data:
            issues.append((str(path.relative_to(root)), "binary or oversized file"))
            continue
        try:
            content = data.decode("utf-8")
        except UnicodeDecodeError:
            issues.append((str(path.relative_to(root)), "non-UTF-8 file"))
            continue
        for item in text_findings(content):
            issues.append((str(path.relative_to(root)), item))
    return issues


def git_findings(root: Path = ROOT, *, strict_email: bool = False) -> list[tuple[str, str]]:
    """Reject publishing surnames in commit identities; optionally reject emails.

    Privacy policy gives priority to family names. Existing initial GitHub
    metadata may contain a private email; use --strict-email to fail on that
    separately. No discovered identity values are ever printed.
    """
    def run(*args: str) -> str:
        return subprocess.check_output(["git", "-C", str(root), *args],
                                       text=True, stderr=subprocess.DEVNULL)
    if not (root / ".git").exists():
        return [("git", "Git metadata unavailable; initialize first")]
    try:
        commits = run("rev-list", "--all").splitlines()
        findings: list[tuple[str, str]] = []
        for sha in commits:
            identities = run("show", "-s", "--format=%an%n%cn%n%ae%n%ce", sha).splitlines()
            if any(FULL_CREDIT_NAME.search(name) for name in identities[:2]):
                findings.append(("git commit " + sha[:12], "private surname in commit identity"))
            if strict_email and any(not (mail.lower() == "noreply@github.com" or
                 mail.lower().endswith("@users.noreply.github.com"))
                 for mail in identities[2:]):
                findings.append(("git commit " + sha[:12], "non-noreply email in commit identity"))
        return findings
    except (FileNotFoundError, OSError, subprocess.CalledProcessError):
        return [("git", "unable to inspect Git history")]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan NeuroGenesis sources and optional Git history")
    parser.add_argument("--git", action="store_true", help="reject private family names in Git commit identities")
    parser.add_argument("--strict-email", action="store_true", help="additionally require noreply email in all Git commits")
    args = parser.parse_args(argv)
    findings = source_findings(ROOT)
    if args.git or args.strict_email:
        findings.extend(git_findings(ROOT, strict_email=args.strict_email))
    if findings:
        for path, issue in findings:
            print(f"PRIVACY FAIL: {path}: {issue}", file=sys.stderr)
        return 1
    print("PRIVACY OK: source data and requested commit metadata checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
