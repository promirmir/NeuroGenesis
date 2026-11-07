# Privacy, provenance and operator authentication

## Public credit

**Miron przy pomocy AI.** No surname, personal email, phone number, address or identifying local workstation paths are permitted in tracked files, snapshots, documentation, issues or commit messages. Public GitHub username and its noreply address are used solely for repository operations.

## Git history is part of the publication

Changing README or `origin.py` does not remove previous content from commit trees, author metadata, PR diffs, forks or caches. The clean rebuild starts from a **single new root commit** by `SAFE_PUBLISH.ps1`, with explicit public GitHub noreply author and committer. The current remote SHA is pinned so the script cannot silently overwrite newer work. The initial old root commit in the new repository currently contains a private account address in its metadata and must be replaced. Rewriting does **not guarantee global erasure**.

## No name-based authentication

A person typing a public or private name cannot prove they control this project. Future operator commands will require locally provisioned cryptographic credentials or passkeys. No authentication or privileged network functions currently exist. Never use a personal name as a password, access token, or seed.

## Privacy gates

- Run `python -m scripts.privacy_audit` before any commit.
- Run `python -m scripts.privacy_audit --git` after the repo has been initialized.
- Reject ordinary email addresses, PEM private keys, common token prefixes, and local user-profile paths in the source tree. All tracked commit author/committer emails must end with `@users.noreply.github.com`.
- Keep tests, rollback guidance and research checkpoints. A privacy fix must not silently change behavior.
- Remove old snapshots that disclose personal information from public files; migrate privately by loading and saving through the current version.

## Residual exposure

Public Git hosting may have cached or indexed previous commits and references. Old forks, clones, archives, and search engine caches cannot be erased by a new Git commit. For sensitive data removal follow GitHub's documented support pathway, with separate verification of any remaining links.
