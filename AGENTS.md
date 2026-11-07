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
6. Verify **no family name** appears in source or commit author/committer identity; run `python -m scripts.privacy_audit --git` and require green GitHub Actions on Python 3.11, 3.12 and 3.13; merge only verified changes. Record commit SHA, benchmark conditions and known limitations.
7. Update `docs/PROJECT_STATE.md` and append to `docs/DEVELOPMENT_LOG.md` after each merged milestone so the next conversation resumes from verified facts, not promises.
8. If interrupted, leave a branch and PR with explicit state, failed checks, next actions and rollback notes. Never claim completion of unmerged or untested work.

## Current verified foundation

- **v0.2**: deterministic CPU-only sparse spiking neuron simulation, structural growth/pruning, JSON snapshots, sensory hashing, self-state telemetry and a basic self-supervised next-input prediction control.
- No semantic comprehension, natural conversation, open internet reading, autonomous source edits, GPU training or validated consciousness.
- Follow-up work: `#3` out-of-distribution and retention tests, `#4` read-only web sensory inputs, `#5` grounded language and functional self-modeling.

For the latest authoritative status and reproduction commands see **`docs/PROJECT_STATE.md`**. Do not change experimental methodology silently.

## Privacy / continuity policy

Public credit is **Miron przy pomocy AI**, with no family name. The old public
repository was deleted; this is its reconstructed replacement. An initial
README commit may retain the GitHub account's chosen email in public commit
metadata; do not claim that a source edit removes it. Set GitHub noreply for
future local commits where possible. The privacy scan blocks private family-name
patterns, secrets and personal contact details in files, plus name patterns
in Git commit identities. E-mail disclosures in existing commit metadata are
reported separately and are not a blocker under the current operator priority.
Do **not** rewrite Git history or force-push without verifying the exact remote
SHA, protecting prior work and user approval of that destructive action.

Current implementation: v0.3 A-B-A benchmark; run `python -m neurogenesis
benchmark --seeds 10 --steps-per-phase 128 --probe-steps 48`. No evidence of
structural growth outperforming fixed architecture. Update benchmark and
recovery docs after every verified merged change.
