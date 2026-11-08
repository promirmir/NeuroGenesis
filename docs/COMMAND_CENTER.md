# NeuroGenesis Command Center — implementation contract

**Public credit: Miron przy pomocy AI.** This document starts the **additive** professional desktop migration; it is not a shipped Qt application or a screenshot.

## Architecture and release isolation

- Keep existing `desktop_launcher.py`, Tkinter desktop and `NeuroGenesis.exe` unchanged as the production baseline until a new, separately testable shell passes Windows frozen-EXE regression.
- Candidate frontend: **PySide6 / Qt** optional dependency only; validate exact version, LGPL/commercial terms, required notices, dynamic linking, redistribution of Qt components and package size before integrating into default EXE. The current default core must remain third-party-dependency free.
- Runtime boundary: UI never directly executes web requests on the main thread. An application-service layer exposes immutable snapshots and typed events (brain state, current source/study status, evidence, training jobs, hardware telemetry). GUI event adapters marshal updates safely onto the UI thread.
- Identity/privacy: local-only at startup, HTTPS off by default, no external costs, untrusted pages never interpreted as commands. Preserve `%LOCALAPPDATA%\\NeuroGenesis\\experiences.sqlite3` without destructive migration; do not copy private content to public artifacts.

## Navigable modules and true telemetry

1. **Dashboard:** version/build SHA, real SQLite health, CPU state and verified model checkpoint, effective permissions, last jobs and actual measured research counts.
2. **Conversation:** dominant flexible chat layout with contextual thread, typed `explicit_local_teaching`, `source_evidence`, `sensory_acknowledgement` and future `model_inference` badges only when backed by the corresponding real backend.
3. **Research Lab:** human-approved topic, source plan, queue, robots/rate limits, tried/saved/blocked/errors, stop; pause/resume only after worker supports safe checkpoint/cancellation.
4. **Brain Monitor:** actual `Brain.traces` and learned-parameter metadata; pan/zoom sparse graph and time-series after instrumentation exists. No invented firing pulses or consciousness score.
5. **Training & Hardware:** optional authenticated local worker, measured step/s, loss, train/validation, CPU/GPU/VRAM when actually available; no imaginary progress bars.
6. **Sources & Memory:** locally indexed passages, timestamps/hashes/versions, rights and evidence links, safe deletion/backup, unknown/contradictory-source indicators.
7. **Settings & Diagnostics:** network opt-in, budgets, bounded logs, memory integrity, update provenance/rollback.

## Dark visual system

Use declarative design tokens (not repeated widget styles): charcoal surfaces, high contrast text, limited cyan/teal data accent, neutral density tiers, semantic error/warning states with text labels. Scale via Qt high-DPI and system font metrics. Layout supports 720p minimum through large 4K monitors, keyboard access, loading/empty/error states, thousands of text passages through virtualized models and no blocking worker.

## Implementation order and non-regression

1. Build a read-only, headless-testable service adapter for existing core + knowledge; no Qt dependency in it.
2. Add an optional PySide6 shell behind a separate explicitly requested launcher, first with functional Overview/Conversation/Sources using real service data; do not substitute a static mockup.
3. Add research task manager, logs, stop/cancel, non-blocking Qt signals, responsive data views; instrument real telemetry for training and brain monitor.
4. Add license verification, Windows package size audit, smoke/manual high-DPI testing and data migration rollback. Only then consider switching the latest Windows EXE entrypoint.

Success is a functioning desktop over actual knowledge and neural services with passed Windows GUI and privacy tests, not a visually polished but disconnected prototype.
