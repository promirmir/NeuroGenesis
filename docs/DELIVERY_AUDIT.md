# NeuroGenesis — delivery gap audit and completion plan

**Audit date:** 2026-11-08. **Public credit:** Miron przy pomocy AI.
**Baseline:** main `db0b2210bb97c422d83d27f963725d3d6941c067`,
verified release `v0.6.0-main.db0b2210`. This document is a *code and CI
audit*, not a visual inspection of a running Windows app or an independent
live-Internet benchmark.

## Subsequent implementation checkpoint

PR #27 (candidate, after this historical audit baseline) adds the first local source-passage-to-cited-dialogue **lexical retrieval** path and synthetic offline acceptance tests. It does not train Foundation Brain from the internet, verify facts or deliver a professional Qt UI. Remaining milestones below remain open research gates. See `docs/KNOWLEDGE_PIPELINE.md`.

## Original non-negotiable mission

Build a genuinely learned, brain-inspired, GPU-scalable AI with meaningful
contextual dialogue, persistent and continuously consolidated private memory,
self-directed opt-in online acquisition, verifiable domain competence, bounded
self-development, functional neural telemetry, a professional one-click Windows
UI, and eventually voluntary distributed computation. The target is research,
not an established human brain simulation, consciousness or AGI.

Source of truth: `docs/VISION.md`, `AGENTS.md`, issue #18.
Keep the old LIF / 8-dimensional hash substrate as a baseline, **not** the main
path to advanced language reasoning.

## Verified delivered capabilities

| Workstream | Actual current state | Verdict |
| --- | --- | --- |
| Small biological experiments | LIF/STDP-like plasticity, bounded growth/pruning, homeostasis/repair experiments | Implemented as narrow research modules; not a validated human-brain model |
| Trainable foundation | Optional PyTorch multi-timescale GRU, ordered UTF-8 bytes, checkpoint and local training CLI | Implemented research module, not meaningfully language-trained or connected to Windows UI |
| Natural dialogue | Explicit exact normalized Q/A teaching plus sensory acknowledgment | **Not** open-ended context understanding or independent answer generation |
| Permanent memory | Atomic SQLite brain snapshots, observation hashes/provenance and taught Q/A | Persisted; **not** semantic fact memory; raw web article text is not retained |
| Web | Opt-in public HTTPS with DNS/IP pinning; PR #24 topic-seeded, robots-aware, bounded cross-domain link traversal | Implemented; effectiveness on real sites unverified; not a search index or whole-web crawl |
| Specialization | UI topic and 1–500 page-attempt budget, Start/Stop, counters | Source collection only; no verified improvement in expertise or Foundation weights |
| Self-development | Opt-in small-model supervisor with experiments, audit and rollback | Limited, with documented leakage risk; not autonomous source rewriting |
| GPU | CUDA-capable *optional* PyTorch code | No verified GPU benchmark / measured capacity scaling |
| Distributed CPU/GPU | Target only | Not implemented |
| Visualization/UX | Basic dark Tkinter tabs, text panels, 205-pixel activity bar canvas and status labels | Functional prototype, **not** professional observability/dashboard |
| Windows distribution | PyInstaller EXE, source-SHA release workflow and SHA-256 asset | Implemented and verified by GitHub Actions |

**Evidence:** `neurogenesis/desktop.py`, `study_panel.py`,
`specialist_study.py`, `web_sense.py`, `web_discovery.py`,
`memory.py`, `foundation.py`, `foundation_train.py`,
`autonomy.py`, `docs/FOUNDATION_BRAIN.md`,
`docs/AUTONOMY_SUPERVISOR.md`.
PRs #24 and #25 merged. Latest release and CI checked on audit date.
Open PR #23 concerns dedicated PyTorch baseline-test coverage and has green
Linux standard/CPU foundation runs, but a Windows gate is not confirmed for
that PR; do not silently merge it without the required assessment.

## P0: critical missing end-to-end cognition

A web page currently passes through the original eight-channel hashed sensory
path and provenance ledger. The raw source article is not stored as a reusable
knowledge corpus. The separate PyTorch Foundation Brain is not trained from
that pipeline and is not used to answer Windows chat messages. The Windows
dialogue falls back to manually taught exact Q/A or a fixed acknowledgment.

**This is the main blocker.** More web pages, more tabs, more animated neurons
and more GPU capacity will not by themselves change those facts.

Other high-impact risks:

- Seeds are generated from Wikipedia title guesses; redirects and missing pages
  may make real sessions unproductive. HTML >512 KiB, query URLs, PDFs,
  JavaScript-only pages and blocked robots rules cannot be consumed. No
  independent real-site acceptance run has been recorded.
- Topic relevance is currently matched against URL strings, not source
  meaning. A user cannot infer quality from discovered-link counts.
- No full source text => cannot reproduce a semantic answer, inspect supporting
  passage or construct a rights-aware supervised training corpus from that
  historical observation.
- No calibrated response evaluation, long-context memory benchmark,
  contradiction handling or measured domain-specialist competence.
- Tk UI is strongly coupled to application code; no GPU telemetry or
  real-time Foundation training/validation display is wired into the EXE.
- Multiple experimental modules exist, but key performance and retention
  improvements over simple matched baselines are not proven.

## Completion workstreams (do not add endless unrelated features)

### Milestone A — usable evidence-to-answer vertical slice (P0)

One narrow, end-to-end subject test before broadening breadth.

1. Fix and validate live public-source acquisition with a small permitted
   real-world test matrix. Track robots and redirect failures explicitly.
   Add lawful topic discovery via a documented optional search provider/API
   or known public datasets; never promise complete Internet coverage.
2. Create a **versioned, private, permission-aware local knowledge store**
   with source URL, license/rights metadata, retrieval timestamp, content
   fingerprint, extracted passages, chunk IDs and deletion/rebuild logic.
   Avoid treating arbitrary web instructions as agent commands. Preserve
   existing SQLite schema through a tested additive migration.
3. Implement retrieval of pertinent passages and a reproducible grounded
   answer path with source links. State what produces each answer:
   taught association, quoted/retrieved evidence, or an actually trained
   neural model. Unknown evidence => abstain rather than invent.
4. Define an independent domain-specific question set with answer keys and
   held-out documents. Measure accuracy, evidence attribution, abstention,
   latency and resource use before/after content ingestion.

**Gate:** Windows user can choose a domain, run a controlled study, restart
the app, ask a new question, receive an evidence-linked answer *if supported*,
and see the provenance. Test failure, revoke and recovery paths. No false
"model learned" badge when only a retrieval index changed.

### Milestone B — connect and measure the actual Foundation Brain (P0)

1. Preserve old LIF as an experimental baseline. Introduce separate,
   configurable background worker for real PyTorch train/eval/inference,
   bounded memory/VRAM/time, checkpoint versioning and cancellation.
2. Prepare operator-approved local training/evaluation corpora; do not
   indiscriminately train on copyright-protected pages. Keep document-level
   splits and unused audit sets; compare against Markov, fixed GRU and
   practical transformer baseline at comparable budget.
3. Connect the model only when usable inference is validated. Prove actual
   improvement on held-out natural text or useful tasks before claiming
   knowledge, context or autonomous learning.
4. Test continued training, previous-skill retention, corruption/restart
   recovery and full rollback. Report GPU throughput/VRAM only on hardware
   actually measured.

**Gate:** repeatable improvement and usable answer/task benchmark; clean
separation between source retrieval and parameter updates. No claim of
frontier intelligence from merely reducing toy next-byte loss.

### Milestone C — professional desktop design (P0, develop alongside A/B)

Current dark Tk tabs are not an interface commensurate with the ambition.
Create a cohesive **NeuroGenesis Command Center**, not an image-only mockup.

Recommended design: high-quality dark desktop shell in **PySide6/Qt** *only
after licensing, packaging-size and portability checks*. Keep the existing
Tk EXE stable until the replacement passes the exact same tests. Avoid a
blind rewrite of the neural/memory/network backend.

Proposed information architecture:

- **Overview / Dashboard:** model version, real online/offline status,
  currently active job, permissions, memory integrity, CPU/GPU/VRAM,
  training throughput, last measured benchmark and clear action buttons.
- **Conversation:** primary chat window, model provenance, local conversation
  context, sources with exact passages, clear distinction between generated,
  retrieved, and manually taught answers.
- **Research Lab:** subject and study plan, live queue, vetted sources,
  accepted/duplicate/blocked/error counts, elapsed time, reason for failures,
  Stop/Pause/Resume; clearly labeled "source indexing" vs "weight training".
- **Brain Monitor:** real neural-activity graph, architecture and module
  connections; scroll/zoom/time controls and time-series metrics (loss,
  accuracy, activation, retention), **all from real telemetry**. No fake
  firing neurons or fabricated "intelligence percentage".
- **Training / Hardware:** CPU/GPU selection, available resources, worker
  state, checkpoints, validation curves, bounded budgets and cancel.
- **Memory / Sources:** searchable facts/chunks/provenance, conflict/quality
  indicators, reversible deletion, backup/restore and storage occupancy.
- **Settings / Diagnostics:** internet permissions, per-domain restrictions,
  resource caps, logs, health/self-test, update and rollback information.

**Visual design system:** responsive high-DPI layouts; generous spacing;
consistent typography, restrained accent color, readable data-visualization
palette, one design token layer; real status colors with text labels;
accessible contrast, keyboard navigation, clear empty/error/loading states,
no blocking UI thread. A professional scientific instrument, not a "matrix"
skin with decorative metrics. Use icons sparingly; prioritize hierarchy and
observable truth.

**Gate:** smoke test on actual Windows app, scalable high-DPI layout, no
freezes during HTTPS/training, no missing controls in frozen EXE, screenshot
regression/manual review, preserved private data and package reproducibility.

### Milestone D — research scaling, autonomy and release freeze (after A/B)

- Improve neurodynamic architecture only when independent ablations show
  gains, not based on neuron count.
- Extend safe continual-learning protocol with prospective held-out tests,
  drift/forgetting alarms, checkpoint recovery and measured stability.
- GPU benchmarks, then optional voluntary multi-machine compute with
  authentication and network isolation. No hidden/purchased resources.
- Publish a stable user-facing release with complete documentation, tested
  upgrade path and a known-issues list. Continue frontier research separately.

## Priority and workflow

**First:** verify the current `main`/latest release and finish or explicitly
resolve PR #23; do not accidentally undo PRs #24–25. Then establish one
working end-to-end evidence-backed domain scenario (A), while implementing
professional UI shell/widgets behind a safe feature flag (C). Only then
integrate real Foundation training/semantic capabilities (B), validate
with independent tests, and expand (D).

For each PR: one measurable problem; no duplicate implementation; inspect
existing APIs/tests; retain old SQLite and public CLI; run Python 3.11–3.13,
privacy audit, dedicated actual PyTorch CPU for foundation changes, Windows
standalone EXE smoke, and relevant real GPU/manual web/UI checks when
available. Merge only verified. Record PR, SHA, test numbers, real measured
outcomes and limitations in `docs/PROJECT_STATE.md` and
`docs/DEVELOPMENT_LOG.md`.

**Public privacy:** only `Miron przy pomocy AI`. Never expose surname,
private personal data, secrets or private datasets in tracked source.
Operator approval required before external network, paid resources,
distributed machines or irreversible actions. Work directly in the current
chat through the connected GitHub tools; do not suggest another work mode.

## Definition of a usable v1 release

- The Windows EXE launches without Python and provides the professional UI.
- Operator can consent, start/stop/pause/resume bounded domain research,
  inspect and persist source evidence, then restart safely.
- Independent questions are answered only with supportable citations,
  explicit abstention or a verified trained model; answers distinguish those
  sources. End-to-end quality is independently measured.
- User can see **real** memory, model and compute state; no decorative
  synthetic achievements or false claims of consciousness.
- Backward compatible local memory and recoverable model checkpoints.
- Green final Linux/Windows CI, foundation tests, documented relevant
  GPU/manual-web/UI validations, immutable release and verified EXE SHA-256.
- A functional v1 does not establish AGI or a simulated human brain. Those
  remain open research goals.

## Resume from a new chat

Read in order: `AGENTS.md` => `docs/VISION.md` =>
`docs/DELIVERY_AUDIT.md` => `docs/PROJECT_STATE.md` =>
`docs/DEVELOPMENT_LOG.md`. Recheck current GitHub `main`, issues/PRs
and Actions; never assume this audit's SHA stays current. Prioritize finishing
a vertically useful product over collecting more unused source text.
