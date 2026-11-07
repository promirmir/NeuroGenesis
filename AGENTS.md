# NeuroGenesis: durable agent / developer handoff

**Read this file first in every new chat, automation, agent session or developer handoff.** Source of truth is `promirmir/NeuroGenesis` on GitHub (`main`), not an assistant's recollection.

## Immutable project intent (human-governed)

- **Official credit: Miron przy pomocy AI.** No personal surname or private contact information belongs in source, tests, docs, commit metadata or pull requests. Attribution is stored in `neurogenesis/origin.py` and embedded in new snapshots.
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
6. Verify privacy of commit authors/committers (public GitHub noreply only), run `python -m scripts.privacy_audit --git` and require green GitHub Actions on Python 3.11, 3.12 and 3.13; merge only verified changes. Record commit SHA, benchmark conditions and known limitations.
7. Update `docs/PROJECT_STATE.md` and append to `docs/DEVELOPMENT_LOG.md` after each merged milestone so the next conversation resumes from verified facts, not promises.
8. If interrupted, leave a branch and PR with explicit state, failed checks, next actions and rollback notes. Never claim completion of unmerged or untested work.

## Current verified foundation

- **v0.4**: deterministic CPU-only sparse spiking neuron simulation, structural growth/pruning, JSON snapshots, sensory hashing, self-state telemetry and a basic self-supervised next-input prediction control; synthetic A-B-A benchmark and SQLite episodic memory with atomic brain-state persistence.
- No semantic comprehension, natural conversation, open internet reading, autonomous source edits, GPU training or validated consciousness.
- Follow-up work: `#3` out-of-distribution and retention tests, `#4` read-only web sensory inputs, `#5` grounded language and functional self-modeling.

For the latest authoritative status and reproduction commands see **`docs/PROJECT_STATE.md`**. Do not change experimental methodology silently.

## Privacy / fresh-history policy

The previous public repository was deleted after private commit-author metadata became visible. This reconstruction must publish a **single fresh root commit** using only a valid GitHub noreply address. Never use a connector write method that chooses an unverified account email implicitly. Check remote commit metadata before any subsequent write; review PR diffs and CI logs for personal information. If a privacy check fails, stop rather than publish. Public credit: **Miron przy pomocy AI**. See `docs/PRIVACY_AND_AUTH.md`.

## Durable memory caution

The local SQLite experience database is **not on GitHub**; a new computer or
chat restores the code but not personal local experience data. Back it up
privately if continuity of learned neural state matters. `forget-event` is not
neural unlearning. Do not claim meaningful language understanding or mental
awareness because the database can recall exact hashes.
