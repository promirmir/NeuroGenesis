# Privacy, provenance and operator authentication

## Public credit

**Miron przy pomocy AI.** No surname, email address, phone number, street address or identifying local workstation paths may appear in tracked files, snapshots, documentation, issues or commit messages. Git **author/committer display names** must remain safe public aliases. The operator explicitly accepted visibility of account emails in **Git commit metadata** on 2026-11-07; this limited permission does not authorize posting addresses in source or issues.

## Git history is part of the publication

Changing README or `origin.py` does not remove previous content from commit trees, author metadata, PR diffs, forks or caches. The current repository has a live, merged history and **must not be rewritten by old fresh-root publishing scripts**. The historical Git email visibility was explicitly accepted by the operator, while author display names and public source must remain free of private surnames and secrets. An optional future remediation of historic metadata requires separate, reviewed authorization; rewriting alone does not guarantee erasure.

## No name-based authentication

A person typing a public or private name cannot prove they control this project. Future operator commands will require locally provisioned cryptographic credentials or passkeys. No authentication or privileged network functions currently exist. Never use a personal name as a password, access token, or seed.

## Privacy gates

- Run `python -m scripts.privacy_audit` before any commit.
- Run `python -m scripts.privacy_audit --git` after the repo has been initialized.
- Reject ordinary email addresses, PEM private keys, common token prefixes and identifying local user-profile paths in tracked source. **Git commit email values are permitted by operator consent; Git author/committer names must still use safe aliases.** The optional `--strict-email` audit can be used for stricter policies but is not the current gate.
- Keep tests, rollback guidance and research checkpoints. A privacy fix must not silently change behavior.
- Remove old snapshots that disclose personal information from public files; migrate privately by loading and saving through the current version.

## Residual exposure

Public Git hosting may have cached or indexed previous commits and references. Old forks, clones, archives, and search engine caches cannot be erased by a new Git commit. For sensitive data removal follow GitHub's documented support pathway, with separate verification of any remaining links.
