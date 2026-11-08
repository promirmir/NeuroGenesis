## Verified handoff — November 8, 2026 (supersedes historical "candidate" notes)

- Current source `main`: `6a45379c2310bc0622b932e21406feddbdbdcd4d`. PRs #32, #33, #34 merged after all appropriate CI: Python 3.11–3.13, privacy, genuine PyTorch CPU, actual Qt Windows/Ubuntu, old frozen Tk EXE and optional frozen Qt technical smoke.
- Real trained Foundation weights now support isolated local, trust-gated next-byte inference (#32), two-checkpoint old/new numerical regression testing (#33; synthetic candidate rejected), and **true weight continuation** from a prior local trained checkpoint to a new candidate output (#34; 2+2-step actual CPU test). This is byte prediction, NOT independently validated semantic conversation.
- Last measured fictional continuation CE `5.6478154→5.5607319` nats over 2 resumed steps, weaker than first-order Markov. The previous .pt SHA remains intact. AdamW optimizer moments restart, no silent checkpoint deployment, no automatic public-web weight training.
- Do not repeat these already merged implementations; read `docs/PROJECT_STATE.md`, `docs/FOUNDATION_INFERENCE.md`, `docs/RETENTION_GATE.md`, `docs/KNOWLEDGE_TRAIN.md` before next task. Qt redistributable not approved/published; existing Tk EXE remains default. Newest release and post-merge CI must be checked live.
- **Next P0**: licensed natural QA/semantic-context evaluation versus strong controls, independently unused audit corpora, retention/candidate rollback without regressing previous knowledge; then actual RTX/CUDA measurement and Qt licensing/package distribution. No AGI, consciousness or human-brain imitation asserted.

## Active safe weight continuation (2026-11-08) — PR candidate

- Main baseline `fd4ab6a723baad237d583d62991dbfdcd84b3f74`: PR #33 old/new retention audit merged after real PyTorch CPU, Linux Python 3.11–3.13/privacy and frozen Windows EXE. Synthetic audit **rejected** model candidate; this is the desired gate behavior.
- Branch `feat/safe-foundation-continue-learning-20261108` adds explicit, bounded continuation of **trained Foundation Brain weights** from trusted private checkpoint on newly approved corpus, to a separate fresh .pt file; old weights/checkpoint and private SQLite preserved, no automatic chat model replacement. Optimizer state **resets**; only model weights/step counter resume. Qt Training has opt-in resume control. See `docs/KNOWLEDGE_TRAIN.md` and `docs/RETENTION_GATE.md`.
- Candidate pending full CI (Python 3.11–3.13, privacy, actual PyTorch CPU, Qt Windows/Linux, old Tk frozen EXE, Qt frozen EXE). Do not call merged or released until tests verify. CUDA physical benchmark, semantic QA and Qt licensing distribution remain open.

## Active continuation — checkpoint retention and evaluation (November 8, 2026)

- PR #32 **merged** to main `ec5bc9fcfdbc2fa7c940e33fc8b090a48ed610b7`; actual trained-weight candidate next-byte inference exists in `foundation_infer.py`, but **is not deployed as sourced conversation**. Current feature branch: `feat/foundation-candidate-retention-audit-20261108`.
- New candidate `foundation_gate.py` compares actual incumbent and candidate PyTorch checkpoints on separate old/new local audit documents, requiring measured old-skill retention AND new-task gain; zero automatic promotion, no claims of semantic chat, default Tk unaffected. See `docs/RETENTION_GATE.md`. Operator asserts audit data independence and rights; cannot assume truth or no leakage.
- Required before merge: all Python 3.11–3.13/privacy checks, actual PyTorch CPU dedicated suite, Qt Windows/Ubuntu, frozen Tk and Qt Windows EXE checks. Keep private snapshots off public GitHub; no physical CUDA benchmark or Qt redistributable release yet.

## Active checkpoint inference pilot — PR candidate, November 8, 2026

- Fresh main baseline `0afcb2b37ee908c4810b6c545e8833ebef9fd787`; all prior work #23–#31 merged. Continue from branch `feat/foundation-inference-lab-20261108` without replaying old implementations.
- New `neurogenesis/foundation_infer.py` and Qt Training-only lab actually decode **trained FoundationBrain weights** into a bounded byte continuation; output can be unintelligible, is **ungrounded** and never becomes a cited or normal chat reply. Requires explicit local checkpoint trust, no network or SQLite mutation, separate background worker, ≤64 bytes, optional PyTorch. See `docs/FOUNDATION_INFERENCE.md`.
- Dedicated *real* PyTorch CPU test plus Python 3.11–3.13, Qt Windows/Linux, Tk frozen EXE, Qt frozen EXE and privacy gates **must pass before merge**. No physical GPU test, no Qt redistributable legal clearance and no semantic competence claim. Resume with checks and resolve failures, then document verified merge SHA.

## Verified continuation checkpoint — November 8, 2026

- `main` confirmed source integration merge `334b1afc842f662b422b8ca81404c3fd75874523`; PRs #23/#27/#28/#29/#30 completed. The previous "PR candidate" and pending-CI sections below are historical snapshots, NOT current project status.
- Reproducible synthetic real PyTorch CPU held-out byte CE `5.7385941651 → 5.5994535677` after 3 steps; Markov baseline `1.7341137780` remains much stronger. **Never claim model has learned semantic conversation or surpassed simple baseline**. Source rights per revision remain operator assertions, not verified licenses.
- Dependency-free legacy Tk Windows EXE and private SQLite remain; optional Qt UI actual source/Windows frozen build works in CI but Qt bundle has not been published pending legal notices. No physical CUDA benchmark. Start from `docs/PROJECT_STATE.md`, `docs/KNOWLEDGE_TRAIN.md`, `docs/COMMAND_CENTER.md`; next work: independent semantic/retention evaluation and controlled inference before any v1 status.

# NeuroGenesis: durable agent / developer handoff

**Read this file first in every new chat, automation, agent session or developer handoff.** Source of truth is `promirmir/NeuroGenesis` on GitHub (`main`), not an assistant's recollection.

## Audyt dostarczenia i jakości (2026-11-08)

Read [docs/DELIVERY_AUDIT.md](docs/DELIVERY_AUDIT.md) after [docs/VISION.md](docs/VISION.md). It reconciles original intent with verified v0.6.0 code/CI and prioritizes **a real end-to-end knowledge-to-answer path plus a professional Windows GUI** over adding more disconnected features. This is a source audit, not proof of real-world internet coverage or of AGI. Follow the measurable release gates and preserve release/backward compatibility.

## Active PR and continuation — 2026-11-08

- PR #23 is **merged** on main `66f3d61fa1696aaeeb3c33c0d035100a9aaacba1`; required Python 3.11–3.13, real PyTorch CPU, Windows frozen EXE and privacy checks passed.
- PR #27 is the **candidate** first internet evidence→private SQLite passage index→quoted citation in normal Tk conversation, with restart persistence, duplicate/revision/deletion behavior and abstention on missing evidence. Important privacy change: extracted public page passages (up to 6000 chars) are saved locally, not just fingerprints. Not neural weight training or independent source validation. See `docs/KNOWLEDGE_PIPELINE.md`, and do not claim a release until final CI/EXE and publication pass.
- `docs/COMMAND_CENTER.md` defines the staged optional PySide6 frontend; **no professional Qt UI is implemented yet**. Keep existing production Tk EXE stable and local memory private.

## Current PR candidate — optional Command Center Qt shell

- PR #27 merged on main `a284aae07934fee42db55897a8cde4eb3312713e`. Real source passage retrieval is integrated with existing Windows chat; evidence retrieval is **not Foundation model weight training**.
- Branch `feat/command-center-qt-service-20261108` adds an optional real PySide6 Command Center with actual memory/chat/research/brain views and a dependency-free service adapter; the default Tk EXE remains unchanged. Read `docs/COMMAND_CENTER.md`. Dedicated real Qt CI on Windows/Linux, Python 3.11–3.13, Windows EXE regression, privacy and packaging/legal checks are mandatory before calling this a release.
- Future actual Foundation Brain inference and GPU gains remain open; training panel is truthful about not being connected. No claim of humanlike cognition.

## Optional Qt frozen Windows validation now in progress

- PR #28 merged to main `2bd5af5a1db70dee8566f848a41d5024e8fa8bba` with real Qt offscreen Windows/Linux CI, Python 3.11–3.13, PyTorch CPU, Windows Tk EXE and privacy green. Optional GUI source exists; not automatically included in published EXE.
- Branch `ci/qt-windows-frozen-smoke-20261108` introduces separate `command_center_launcher.py` and frozen Qt `--self-test` plus technical onedir PyInstaller CI. Do not claim Qt package released; audit LGPLv3 obligations and redistribution notices first. Preserve original Tk EXE and SQLite and never publish private data. See `docs/COMMAND_CENTER.md`.

## Active rights-gated Foundation training integration — PR candidate

- PR #29 merged `9388e19356c2d7f49ffdd1a72d0996d3d89986b0`, technical Qt Windows onedir EXE smoke passed (tested exe SHA256 `2d563058b985f169ae04b39f8674f1f5d2a5fc85af0dbfc6d32b86c3501ac3b8`, bundle 111.95 MiB). **No Qt downloadable release** without LGPL/notices review. Legacy Tk app remains verified.
- Candidate branch `feat/approved-web-foundation-train-20261108` links only **operator-approved source versions** to actual local Torch weight training, with document-level holdout, measured cross-entropy against Markov, cancellation, no auto-install and explicit rights confirmation. Training UI displays real losses, not intelligence scores. Read `docs/KNOWLEDGE_TRAIN.md` and run dedicated real CPU, Windows Qt/Tk, privacy tests before merge. Neural semantic conversation and independent factual validation remain open.

## Highest-priority permanent contract

Read [docs/VISION.md](docs/VISION.md) before planning new changes. The user explicitly wants a powerful and novel self-learning, GPU-scalable, human-neurobiology-inspired cognitive engine, permissioned live Internet knowledge perception, meaningful Windows conversation, rich realtime visual observability, long-lived memory and continuity across chats. A 24-neuron/8-channel toy or a list of handwritten replies is not the target; retain those as research baselines only. No unverified promise of human brain emulation, consciousness or global breakthrough is allowed.

A live browser session or an unattended PC alone does NOT produce uninterrupted asynchronous coding. Persist active code/CI state to GitHub and use an authorized scheduled agent task when available; never promise overnight work unless an actual automation is created.

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

## Strategic reset — high-capacity Foundation Brain (issue #18)

User explicitly rejected treating eight hashed text channels and a few dozen spiking neurons as progress toward a leading AI. Keep the v0.5.6 one-click Windows executable, existing SQLite memories and original small LIF research as a stable backward-compatible baseline. PR #17's eight-channel temporal experiment was **closed without merge**, with branch preserved for comparisons. The new priority is a genuinely trainable, scalable self-supervised neural foundation: ordered symbols with learned embeddings, fast/slow recurrent representations, latent prediction, independent natural-language data, CPU/GPU performance and reproducible checkpoints. See docs/FOUNDATION_BRAIN.md and issue #18. Do not equate bigger models or toy loss reductions with general intelligence or human-brain equivalence.

The optional research implementation uses real PyTorch but must not be imported by the default Windows EXE. GitHub foundation-cpu CI must actually install PyTorch and exercise learning; default CI skips optional tests only for compatibility and **does not** count as validation. Do not merge without both standard and dedicated CPU CI, and do not publish a new Windows release claiming language understanding until there is a trained model with independently measured practical utility.

## Current v0.6.0 candidate: optional public HTTPS perception

The next verified feature integrates read-only **explicitly enabled** public HTTPS input into the existing local spiking brain using DNS/IP pinning, TLS hostname checking, no redirects, limited text extraction, deduplicated source SHA-256, atomic SQLite provenance and a Polish Windows Internet tab. See docs/INTERNET_SENSE.md. Refresh can run every five minutes only for a manually approved URL and only while the UI remains open. Does **not** yet feed the larger trained Foundation Brain or prove semantic comprehension. Keep network OFF on startup and prohibit untrusted web instructions from being executed. Maintain real isolated unit tests for private IP/SSRF and Windows frozen EXE smoke.

## Merged PR #24 — bounded multi-domain autonomous specialist research

Merged to `main` via `578222800c5adc73c0a756352b5bef405535252a` after verified PR Python 3.11–3.13, privacy and Windows EXE CI; the Windows **Specjalizacja** panel accepts a subject and an operator-controlled budget (1–500 pages; default 120). After explicit HTTPS permission, a bounded researcher starts from Polish/English Wikipedia subject pages, discovers topic-relevant HTTPS links including other domains, checks robots.txt by pinned TLS, enforces crawl/rate/domain/depth limits, records provenance in the existing local SQLite brain, and exposes Stop plus progress. Read `docs/SPECIALIST_STUDY.md`, `docs/PROJECT_STATE.md` and PR #24. This is **not** indexing all of the Internet, external search API, semantic expertise, Foundation Brain gradient training or a completed release. Main Python, Windows standalone EXE and publishing CI succeeded; release `v0.6.0-main.57822280` targets the verified merged SHA and includes the new specialist tab. No real-site crawler success or semantic expertise has been independently benchmarked. Keep existing public author credit first name only.

## Current verified foundation

- **Verified v0.5.5 on main (PRs #10, #12 and #13)**: preserves the v0.4 CPU-only sparse spiking neuron, prediction, JSON snapshots and transactional SQLite episodic memory. Adds experimental homeostasis and bounded memory-guided repair, self-development and capacity growth trials, a native Windows EXE, and an opt-in periodic self-development supervisor that atomically saves the real brain and predictor in SQLite; no autonomous source modification or internet.
- No semantic comprehension, natural conversation, open internet reading, autonomous source edits, GPU training or validated consciousness.
- Follow-up work: `#3` out-of-distribution and retention tests, `#4` read-only web sensory inputs, `#5` grounded language and functional self-modeling.

The permanent Windows binary download must be clearly visible at the top of `README.md` and `URUCHOMIENIE_PL.md`: `https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe`. Release publishing uses a **separate, main-only workflow** after Windows test/EXE verification, not write permission during PR builds. Verify release SHA-256 and source commit before claiming publication.

**Next user-facing candidate v0.5.6** introduces explicitly taught local question/answer recall in the real SQLite/brain transaction. Its answer text is symbolic memory retrieval, **not** language semantics generated by the spiking neural substrate. See docs/TEACHABLE_DIALOGUE.md; keep this distinction in the UI, docs, release notes and benchmarks. Never discard existing private memory when updating EXE.

For the latest authoritative status and reproduction commands see **`docs/PROJECT_STATE.md`**. Do not change experimental methodology silently.

## Privacy / fresh-history policy

The previous repository was deleted after a metadata exposure incident. The operator has now **explicitly authorized visibility of Git author email**, but **not private surnames as display names or personal data in tracked files**. Commits using public alias names are permitted after verifying the resulting Git author/committer names; the historical fresh-root rewrite instructions are obsolete and must NOT be run against current `main`. Keep source privacy auditing and PR/CI checks. Do not force-rewrite history without a separate explicit authorization. Public credit: **Miron przy pomocy AI**. See `docs/PRIVACY_AND_AUTH.md`.

## Durable memory caution

The local SQLite experience database is **not on GitHub**; a new computer or
chat restores the code but not personal local experience data. Back it up
privately if continuity of learned neural state matters. `forget-event` is not
neural unlearning. Do not claim meaningful language understanding or mental
awareness because the database can recall exact hashes.
