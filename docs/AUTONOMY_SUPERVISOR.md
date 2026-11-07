# NeuroGenesis v0.5.5 — transactional autonomic supervisor

**Public credit: Miron przy pomocy AI.** This is an opt-in, bounded neural research feature, not humanlike cognition or autonomous source-code programming.

## What is implemented

The local GUI has an optional AUTO checkbox and a "Przetestuj ulepszenie" button on the Mózg tab. AUTO is OFF on every application start. When enabled, the process checks every 30 seconds whether at least 40 new observations have arrived in the private SQLite ledger. No recurring job runs after the app is closed; no cloud, Internet or remote processes.

Each 40-event window (hashed sensory features, not raw text) is split once into 8 old-skill guard + 16 training + 8 selection + 8 independent audit samples. The existing bounded self-development algorithm compares a portfolio of learning rates on cloned neural substrates. It selects on selection data only, checks improvement on fresh audit data and vetoes unacceptable guard regression. Rejected proposals do not alter the live brain.

On success the actual brain snapshot and its associated online predictor are stored together in a single SQLite transaction, together with an audit entry, monotonic consumed-event watermark and bounded prior-state checkpoint. The next received message advances the SAME brain through the persisted predictor; no parallel orphan brain is created. Until any candidate is accepted, the original v0.4 event path is unchanged. Existing database files remain schema version 1 compatible.

Validation failures roll back the entire transaction and do not erase observations. The Python API AutonomicSupervisor(memory).rollback_last_promotion() restores the previous neural snapshot only BEFORE the brain has processed subsequent observations; otherwise it fails closed to prevent discarding newer learning. It does not alter the separately stored real-life observation ledger.

## Safety and limitations

- No unsupervised Internet, external processes, source edits or cloud charges. Each trial uses at most 40 observed feature vectors and 3 candidate configurations by default.
- Every event ID is used in only one trial window; audit inputs are never recycled. These are local hashed input patterns, not genuinely out-of-distribution tasks.
- SQLite writes are guarded by an IMMEDIATE transaction, snapshots are size validated, and supervisor reports contain only metrics, not raw text.
- This learns next-input predictions from a toy hashed sensory encoder. It is not proof of natural-language understanding, general intelligence or biological fidelity.
- Existing isolated evaluation probes may continue synaptic STDP while freezing their readout; fully frozen probes are a distinct research gate.
- GUI cycles currently run in the Tk event loop and could briefly block the window; production work should use a supervised cancellable worker with a wall-time limit and pre-commit revalidation.
- A valid outcome is rejection for no measured benefit. Do not count rejected proposals as proof of cognitive improvement.
- Local SQLite is NOT encrypted. Never enter passwords or credentials. Keep private backups; GitHub hosts code only.

## Verification

Run the original unit suite on Python 3.11, 3.12 and 3.13 and the Windows PyInstaller one-file EXE smoke test. New tests cover real SQLite atomic promotion, rollback, restart, fail-closed corruption, consumed audit windows, no-data gate and cancellation. No change is releasable until all pass.

Issues: #3, #5, #7, #8 and #9. Public attribution: Miron przy pomocy AI.
