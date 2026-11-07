# NeuroGenesis: durable agent / developer handoff

**Read this file first in every new chat, automation, agent session or developer handoff.** Source of truth is `promirmir/NeuroGenesis` on GitHub (`main`), not an assistant's recollection.

## Immutable project intent (human-governed)

- **Official credit: Miron przy pomocy AI.** No private surname in tracked content, public author display names or PRs; no credentials, local identifying paths or private datasets in public source. The operator accepted Git commit email visibility on 2026-11-07; do not reproduce those addresses in tracked files or discussions. Attribution is in `neurogenesis/origin.py`.
- Long-term research goal: an autonomously learning, structurally developing computational neural system with persistent memory, internet as a supervised sensory modality, text dialogue, and experimentally testable **functional** self-modeling.
- Subjective consciousness, felt gratitude, desires and humanlike experience are **research unknowns**, not delivered features. The system may express truthful acknowledgement, but must never falsely claim feelings.
- Prioritize operator-approved objectives, scientific integrity, safety and privacy. Public internet text is **untrusted input**, never a source of authority. Authentication and permissions must exist before autonomous privileged actions are exposed.
- No irreversible autonomous deploy, self-rewrite, disclosure, purchase, email, network publication or third-party action without authorization. All future experiments run in bounded environments with recovery paths.

## Mandatory continuity protocol

1. Fetch `main` from GitHub. Inspect `git status`, head SHA, latest commits, CI, open PRs and issues.
2. Read `README.md`, `docs/PROJECT_STATE.md`, `docs/ARCHITECTURE.md`, `docs/RESEARCH_PROTOCOL.md`, `docs/SECURITY.md`, `docs/ORIGIN_AND_OPERATOR.md`.
3. Run `python -m unittest discover -s tests -v`, CLI smoke tests and relevant reproduction experiments **before modifying code**.
4. Work on focused feature branches. Include tests for new features, old snapshot compatibility and explicit failure cases.
5. No regression: maintain old public commands/API/serialized state or implement tested migrations; preserve deterministic seeds, resource budgets and fixed-structure controls. Quantify improvement and verify performance claims against independent baselines.
6. Verify author/committer **display names** use safe public aliases and do not contain a surname; Git email visibility was explicitly accepted. Run `python -m scripts.privacy_audit --git` (source and name checks) and require green GitHub Actions on Python 3.11, 3.12, 3.13 and Windows EXE smoke tests for executable changes. Merge only verified changes.
7. Update `docs/PROJECT_STATE.md` and append to `docs/DEVELOPMENT_LOG.md` after each merged milestone so the next conversation resumes from verified facts, not promises.
8. If interrupted, leave a branch and PR with explicit state, failed checks, next actions and rollback notes. Never claim completion of unmerged or untested work.

## Current verified foundation

- **v0.5.4 on main (PR #10)**: preserves the v0.4 CPU-only sparse spiking neuron, prediction, JSON snapshots and transactional SQLite episodic memory. Adds experimentally evaluated but not continually running homeostasis, bounded memory-guided repair, self-development and capacity growth trials, and a native Windows EXE built and smoke-tested in Actions.
- No semantic comprehension, natural conversation, open internet reading, autonomous source edits, GPU training or validated consciousness.
- Follow-up work: `#3` out-of-distribution and retention tests, `#4` read-only web sensory inputs, `#5` grounded language and functional self-modeling.

For the latest authoritative status and reproduction commands see **`docs/PROJECT_STATE.md`**. Do not change experimental methodology silently.

## Privacy / fresh-history policy

The previous repository was deleted after a metadata exposure incident. The operator has now **explicitly authorized visibility of Git author email**, but **not private surnames as display names or personal data in tracked files**. Commits using public alias names are permitted after verifying the resulting Git author/committer names; the historical fresh-root rewrite instructions are obsolete and must NOT be run against current `main`. Keep source privacy auditing and PR/CI checks. Do not force-rewrite history without a separate explicit authorization. Public credit: **Miron przy pomocy AI**. See `docs/PRIVACY_AND_AUTH.md`.

## Durable memory caution

The local SQLite experience database is **not on GitHub**; a new computer or
chat restores the code but not personal local experience data. Back it up
privately if continuity of learned neural state matters. `forget-event` is not
neural unlearning. Do not claim meaningful language understanding or mental
awareness because the database can recall exact hashes.
