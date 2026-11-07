# Security model

## Current v0.1 attack surface

- All commands are local and offline. No network permissions, crawling, arbitrary shell execution or automatic code modifications exist.
- `observe` treats text as inert sensory data; it does **not** interpret instructions within it. It has no semantic understanding.
- Brain and predictor state snapshots are versioned JSON, **not executable pickle**. Loads reject overlarge files, wrong schema, non-finite values, invalid graph indices and invalid dimensions. Snapshots are not encrypted.
- The public repository must contain **no secrets, API keys, authentication tokens, personal datasets or conversation logs**.
- State files should be stored outside the repository or match the `.gitignore` rules; when shared, consider them potentially sensitive.

## Before enabling internet as a sensory interface

Implement all of: explicit user opt-in, read-only allowlists, domain and IP validation against SSRF, redirect re-validation, per-request size and time limits, MIME and charset handling, rate and crawl budgets, privacy boundaries, source attribution, injection-resistant separation of retrieved content from instructions, and logging/disable controls.

## Before enabling autonomous code changes

Require sandbox execution, restricted capabilities, independent test gates, resource quotas, reproducible comparisons, rollback, signed artifact provenance, and explicit human approval for deployment. **Do not let untrusted pages or model output directly execute commands or modify production source.**

## Vulnerability reporting

Avoid posting exploit details and secrets in public issues. Contact repository maintainers through an agreed private reporting channel if one is published. No private reporting endpoint is asserted to exist yet.

## Public source and Git metadata gate

Every commit must use the public GitHub noreply address; source files are scanned for contact data, credentials and local user paths by `python -m scripts.privacy_audit --git`. A source clean-up cannot erase old commit objects or external copies. Do not publish through GitHub write connectors that do not allow explicit commit author/committer identity. The fresh-root publish tool checks the existing remote SHA and refuses unexpected changes.
