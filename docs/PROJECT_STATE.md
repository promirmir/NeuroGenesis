## 2026-11-08 — Multi-domain specialist research, PR #24 MERGED

- Expanded beyond static Wikipedia seeds: safe HTML anchor extraction, topic-filtered BFS across public HTTPS domains, robots.txt policy, crawl-delay, 500-attempt upper budget, 50 domains, 20 attempts/host, depth 3, 600 URL queue, >=5 seconds between page fetches. GUI default 120 attempts and displays domain/discovery/error counts. Existing Internet opt-in controls all network access.
- Manual page reader retains 128 KiB limit; explicit crawler mode has a separately bounded 512 KiB limit. HTML text is capped at 6000 chars and URLs are revalidated through pinned TLS/public IP checks. No unrestricted entire-internet indexing, search API, forum guarantees, semantic understanding or PyTorch gradient training.
- New offline tests validate robots transport, denied paths, failed robots reads, cross-domain discovery, URL filtering, content size, stop and consent. Latest code and Windows tests must be verified on final branch head before any merge/release.
- PR #24 source head `c90126532de97189d3717b4adabb25d71a0b55fe` passed Python 3.11–3.13, source/privacy audit and Windows EXE build/smoke. Squash merged to `main` commit `578222800c5adc73c0a756352b5bef405535252a`. Main Python CI passed, main Windows/release status must be independently verified before claiming a public EXE. See [docs/SPECIALIST_STUDY.md](SPECIALIST_STUDY.md). PR #23 remains separate and open.

## 2026-11-08 — Historical initial PR #24 candidate (subsequently merged)

- The original bounded Wikipedia-only candidate has since been expanded in the above PR #24 milestone to multi-domain link discovery. Retained historical note: GUI-thread SQLite persistence and network-off-by-default.
- No full-Internet indexing, general search API, trained language model, or demonstrated expertise. Follow latest PR #24 details above and `docs/SPECIALIST_STUDY.md`.
- Historical initial source commit: `44e579c71335f6ae02d568aaba99244bb81280dd`; final merged commit is `578222800c5adc73c0a756352b5bef405535252a`. PR #23 remains independent.

# NeuroGenesis — durable project state and recovery

Last documentation review: **2026-11-07**. This file is intended to survive chat interruptions and model/context changes.

## 2026-11-07 — Permanent mission and current v0.6.0 web-sense candidate

- Primary, durable specification: [docs/VISION.md](VISION.md). Build a genuinely capable learned, scalable neural AI with GPU/compute expansion, lifelong learning, private long-term memory, grounded public Internet sensing, useful Polish Windows chat, realtime brain/learning telemetry, and falsifiable neurobiological mechanisms. This is a scientific aspiration, not proof of a breakthrough.
- **PR #19 merged** the genuinely trainable optional PyTorch multi-timescale Foundation Brain in main commit `96d3e04b126712aa6a33029b80ed5bbe7ca20af7`. Dedicated real PyTorch CPU tests, Python 3.11–3.13, and Windows standalone regression/executable smoke all passed. The new model is not yet trained for semantic dialogue and is NOT active in the default EXE.
- **v0.6.0 candidate** adds pinned HTTPS public-text perception in a user-enabled Internet tab. Worker reads max 128 KiB of plain/html, rejects private/DNS-rebinding addresses, redirect and credentials, extracts up to 6,000 chars, persists source URL/UTC/SHA256 with neural brain data atomically. Optional repeat checks only the manually approved URL every 5 minutes. Network OFF by default and no raw downloaded body is kept in SQLite.
- GUI Mózg graph and statistics update automatically every three seconds. Source text is treated as untrusted observation, not commands. No semantic learning or verified language-world model is claimed.
- **Release gate:** this candidate requires all original Linux/Windows CI tests, dedicated Foundation CI, real SQLite web integration and frozen EXE smoke tests before merge and GitHub Release. Until verified, users should download the latest validated v0.5.6 release.

## 2026-11-07 — High-capacity Foundation Brain pivot (issue #18)

- The user rejected the scientific and practical scale of earlier 24-neuron / 8-channel demonstrations. Those experiments are retained as baselines only; do not advertise them as a path to competitive language understanding.
- PR #17 (eight-bin temporal prediction) is **closed without merge**, its feature branch retained for controls. Verified v0.5.6 remains the default Windows EXE; old SQLite schema must not change.
- New research branch must implement a **trainable neural foundation** using ordered symbol representations, fast/slow context, gradient-trained predictive objectives, versioned checkpoints, optional PyTorch/CUDA and dedicated real dependency CI. See docs/FOUNDATION_BRAIN.md.
- No human-like semantic understanding, long-term reasoning, GPU performance gain or general intelligence has been demonstrated by this architecture. Train on permissioned data and run independent, matched compute baselines first.
- Separate foundation CPU CI must be green before merging; when merged, default Windows EXE remains unchanged. Later GUI inference requires actual usable trained weights and authorized local worker resource controls.

## Distribution — permanent latest Windows EXE link

- Public entrypoint: [GitHub Releases — latest](https://github.com/promirmir/NeuroGenesis/releases/latest); direct asset: [NeuroGenesis.exe](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe); [SHA-256](https://github.com/promirmir/NeuroGenesis/releases/latest/download/NeuroGenesis.exe.sha256).
- Trusted `.github/workflows/publish-release.yml` runs only after a green, main-branch Windows standalone EXE build. It downloads the successful build artifact, rechecks its SHA-256 and PE x64 format, validates the main source SHA, and publishes an immutable SHA-tagged release with a separate **contents:write** permission. PRs retain read-only permissions.
- **Verified publication:** GitHub Release v0.5.5-main.bb7b6282 was published on 2026-11-07 with both NeuroGenesis.exe and its SHA-256 (successful release run 42419193604). The stable latest/download link resolves to an actual asset. Later version changes must pass independent CI and create another verified release.

## v0.5.6 candidate — explicitly teachable local responses

- New SQLite associations let the operator teach, correct and delete up to 512 exact normalized question–answer mappings. Teaching and the existing neural sensory path are atomic, but language response text is retrieved from the separately identified symbolic association table, NOT generated by the spiking brain. Normal observations remain text-private by default.
- Native Tk GUI adds a second text field and Teach/Delete controls. EXE self-test and new integration tests cover restart persistence, question normalization, fail-closed corruption, privacy, old message length compatibility and no divergence of the autonomic predictor. See docs/TEACHABLE_DIALOGUE.md.
- This is a candidate until CI and Windows EXE build pass and the PR is merged. Do not call it verified on main prematurely. The existing released baseline is v0.5.5.

## Verified main v0.5.5 — bounded opt-in local self-development

- New neurogenesis/autonomy.py adds an opt-in supervisor using **the same private SQLite brain** as the native Windows app. Every 40 fresh observations are assigned once to separate guard/training/selection/audit roles.
- Successful *measured* candidate adaptation persists the associated trained neural readout and underlying spiking brain atomically to SQLite, with audit record, checkpoint and rollback allowed only before intervening new learning. Rejected candidates preserve the original brain.
- Existing v0.4/v0.5.4 memory files remain compatible; no internet, code-writing, GPU or automatic use of third-party machines. AUTO is OFF by default and only checks while the app is open. See docs/AUTONOMY_SUPERVISOR.md.
- This is a bounded local self-tuning mechanism, **not evidence of autonomous general cognitive development or human-brain equivalence**. Independent OOD and resource/retention benchmarks remain open.
- **Merged PR #12**, main merge commit bbd9c00c557a2e87621cf81c598195109f8e7716. All three Linux CI Python versions and Windows full tests and standalone EXE smoke test passed before merge. Verify fresh main runs before distributing the latest EXE. A follow-up hardening test explicitly refuses databases that contain experiences but lack a neural snapshot.

## Current verified main: v0.5.4 (2026-11-07)

- Merged [PR #10](https://github.com/promirmir/NeuroGenesis/pull/10): code landing commit `ddf6d3aa9c878c6f2ec221289521cf00349f8cba`. This identifier is a historical checkpoint, not a promise that latest `main` will never change.
- **GitHub verified** Linux `research-core-ci` on Python 3.11, 3.12 and 3.13, including original and newly added tests; Windows workflow passed **125 tests** and the PyInstaller onefile EXE runtime `--self-test` with actual SQLite. After merge, main Linux run `42414996746` succeeded and main Windows run `42414996678` succeeded, publishing the downloadable `NeuroGenesis-Windows-x64` artifact (14-day retention).
- `desktop_launcher.py` / `neurogenesis/desktop.py` implement the first native Polish Tkinter app. `%LOCALAPPDATA%\\NeuroGenesis\\experiences.sqlite3` stores local observations and brain state. Internet OFF. No ordinary conversational understanding is claimed.
- Bounded add-on research modules: `homeostasis.py`, `repair.py`, `fingerprint_repair.py`, `self_development.py`, `capacity.py`, `controls.py`, `skill_recovery.py` and `lesion_benchmark.py`. These are **offline experimental modules**, not an autonomous background supervisor, GPU backend or general-intelligence agent.
- Negative research results remain important: previous structural growth was not better than fixed topology on A-B-A; a non-neural Markov predictor greatly outperformed the neural predictor on one simple task. Capacity self-scaling rejected 10/10 proposed expansions when gains were absent. Repair improves task MSE on some narrow synthetic patterns but not on disjoint-cue transfer.
- Public identity policy: credit `Miron przy pomocy AI`; author/committer display names must exclude surnames; the operator accepted visibility of Git metadata emails. Issue #6 closed; continue scanning source and commit names for private information, do not force-rewrite Git history.
- Next milestones: continuous transactional self-development supervisor with real independent holdouts and rollback (#8/#9); safe opt-in read-only internet perception (#4); grounded language (#5) without false cognition claims; independent OOD validation (#3) and structural repair (#7). The Windows EXE must remain one-click and private-by-default.

## Mission

Develop an experimental, self-reorganizing neural substrate that learns over time, later links to controlled internet observations and text dialogue, retains its experiences and can report a calibrated, functional model of its own computational state. Scientific evidence is required for claims of capability. Subjective consciousness is neither currently implemented nor established by a test.

Public project credit: **Miron przy pomocy AI** (first name only). Canonical executable source: `neurogenesis/origin.py` (see `docs/ORIGIN_AND_OPERATOR.md`). Human governance and truthful acknowledgement are design commitments, not implemented authenticated command handling or real feelings.

## Verified implementation and limits

- **v0.4.0 reconstructed baseline** (v0.2 plus project origin/continuity): bounded sparse spiking LIF neurons; STDP-like local plasticity; novelty-triggered bounded growth; weak-synapse pruning; JSON checkpoint deterministic restart; offline text feature hashing (not semantics); observable telemetry.
- Online next-input predictor trained by prediction error, tested on a toy alternating sequence; growth did **not** outperform fixed structure. Reproduce with `python -m neurogenesis predict --steps 600`.
- `python -m neurogenesis compare --steps 128` tests growth/fixed structure under identical inputs (structural metric only).
- `python -m neurogenesis origin` shows canonical attribution and mission. New snapshots include origin metadata; old v0.2 and v0.2.1 snapshots load and upgrade to short attribution on next save.
- **Not built:** autonomous natural language reasoning, real web access, self-updating source, authenticated operator controls, verified subjective consciousness, GPU implementation. Do not silently claim otherwise.

## Continual-learning benchmark v0.3

A -> B -> A synthetic sensory association experiment uses 10 seeds, frozen
readout during independent noisy probes, and paired comparisons of growing and
fixed-structure substrates (not parameter/compute matched). On the local
10-seed run (128 steps/phase, 48-step probes, noise amplitude 0.15), A MSE
after B was **0.14877 (growth)** vs **0.14565 (fixed)**. The lower score for
the fixed architecture means growth did not improve retention. Benchmark results
are preliminary, from a narrow synthetic pattern family; do not generalize.

## Persistent memory v0.4

The `remember` command now saves hashed sensory features + corresponding
spiking brain state atomically in one local SQLite DB, with exact/fuzzy
feature recall and explicit opt-in raw text persistence. `forget-event` only
deletes its log record; it does not reverse learned synaptic state. No semantic
memory or language understanding is claimed. Memory data is not committed to
GitHub: *.sqlite3 and local-data/ are excluded by .gitignore.

## Reproduction from a clean checkout

```bash
git clone https://github.com/promirmir/NeuroGenesis.git
cd NeuroGenesis
python -m unittest discover -s tests -v
python -m neurogenesis compare --steps 128
python -m neurogenesis predict --steps 600
python -m neurogenesis benchmark --seeds 10 --steps-per-phase 128 --probe-steps 48
python -m neurogenesis origin
python -m neurogenesis remember "Pierwsza obserwacja" --db local-data/experiences.sqlite3
python -m neurogenesis recall "Pierwsza obserwacja" --db local-data/experiences.sqlite3
python -m neurogenesis demo --steps 64 --state brain.snapshot.json
python -m neurogenesis status --state brain.snapshot.json
```

Python >=3.11, no third-party dependencies, runs offline on CPU. GitHub Actions executes test jobs on 3.11/3.12/3.13.

## Progress / future work

- Reconstructed v0.1 and v0.2 core plus v0.2.2 privacy handling from a deleted prior repository. v0.3 adds the A-B-A benchmark and readout-frozen isolated probes. v0.4 adds locally persistent event observations and brain state in one SQLite transaction. Earlier PR numbers refer to the deleted repository, not this replacement.
- Issue #3: held-out generalization, retention, at least ten seeds and controlled growth ablations.
- Issue #4: opt-in, read-only internet senses with provenance and SSRF protections.
- Issue #5: grounded text-language interface and functional self-model with measured calibration.
- **Next decision:** prioritize end-to-end integration with independent evidence and no regression: a durable, bounded self-development supervisor (#8, #9), then secure internet sensing (#4) and grounded communication (#5). Continue #3 held-out evaluations as a release gate; do not equate model size with intelligence.

## Resuming in another chat

Give the assistant repository URL `https://github.com/promirmir/NeuroGenesis` and ask it to **read `AGENTS.md` and `docs/PROJECT_STATE.md`, inspect the latest `main` SHA, PRs/issues and Actions, execute tests, then continue the highest-priority verified milestone without regressions**. GitHub contains the state; no prior chat transcript is required for this workflow. Local untracked checkpoint files are **not** on GitHub and must be backed up privately by the operator.

## Non-regression gate

- All existing tests + CLI controls pass; saved-state backward compatibility tested.
- Output metrics are reported with seeds, benchmark/task specification and baseline; no cherry-picking.
- Changes with unverified behavior remain on PR branches; record failures in development log.
- Status document must be updated when capabilities, blockers or active milestone change.

## Privacy gate for every new chat

Public attribution: **Miron przy pomocy AI**. Block any full surname, private
contact details, credentials or secret paths in current tracked files and
commit *names*; e-mail in prior Git metadata may remain visible. CI runs
`python -m scripts.privacy_audit --git`. This is a scanner, not a guarantee
that old Git history or third-party caches have been erased. No forced history
rewrites without explicit verification.


## 2026-11-08 — held-out Markov baseline PR (pending validation)

Added dependency-free `neurogenesis/foundation_baselines.py` and `tests/test_foundation_baselines.py`: disjoint chronological 90/10 split, Laplace-smoothed unigram and first-order Markov next-byte cross-entropy (nats), no holdout fitting, no corpus upload or network. Run: `python -m unittest tests.test_foundation_baselines -v` and `python -m neurogenesis.foundation_baselines --input YOUR_OWN_CORPUS --confirm-corpus-rights`. This is an evaluation comparator, **not** a neural model or a demonstrated language gain. PR branch `research/markov-heldout-baseline`; no CI results or merge asserted. Next: validate Linux Python 3.11–3.13, actual foundation CPU, Windows EXE and privacy checks; compare identical independent holdout with FoundationBrain before reporting any performance claim.

## 2026-11-08 — Full chronological holdout evaluation candidate (unmerged)

Research branch `research/full-holdout-evaluation-20261108` replaces the first-window-only Foundation training metric with a deterministic token-weighted evaluation across all non-overlapping windows in the 10% chronological holdout. Window-boundary transitions are excluded; scored transition and window counts are reported. Real PyTorch regression tests cover weighting, short holdout and non-finite losses. Implementation commits: `9c7d5241ed3a7ec018e10f832e9ace7424ab9289`, `9896530d011e8ecebe84cb72d57c0d2ea6a2e444`. **Pending CI**: Python 3.11–3.13, dedicated Foundation CPU, Windows EXE; do not merge until green. No CUDA benchmark, independent language corpus or semantic understanding demonstrated. This evaluation still uses one adjacent split and is not prospective OOD evidence.
