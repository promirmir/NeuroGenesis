# NeuroGenesis — explicit source knowledge → real Foundation Brain training

**Public credit: Miron przy pomocy AI.** PR candidate: this document describes the implementation, not a released neural language model.

## Scope and scientific meaning

The existing opt-in HTTPS reader and specialist study keep bounded source passages in private local SQLite. The normal conversation retrieves short cited evidence extracts. This PR adds a **separate, explicitly operator-authorized** path that can train actual **FoundationBrain PyTorch parameter weights** on those passages.

Retrieving a quote is still not learning neural model parameters. This pilot self-supervises the Foundation Brain to predict subsequent UTF-8 **bytes**, not to answer questions. It **does not integrate generated neural inference into chat**, learn factual truth, prove semantic understanding or human brain analogy. The trained checkpoint is a private **candidate only**, never automatically promoted or deployed.

## Operator and copyright permissions

1. The Internet/research panels start with HTTPS disabled and require a conscious opt-in. No automatic model training occurs when fetching or observing a page.
2. Every saved source revision begins with `rights_status=unverified`. The operator must review the exact retained text, the site's terms and applicable rights/permissions **before** marking that version as eligible for **local model training**. Public accessibility is not itself permission.
3. Approval and revocation are local SQLite changes; `knowledge_rights_audit` records their UTC time and state. A changed revision is unapproved until reviewed separately. Deleting an event also deletes its rights-audit rows and excerpts, but does not reverse earlier neural learning.
4. Even with prior per-source approval, every training session requires a separate explicit `--confirm-corpus-rights` flag or Qt checkbox. No network, external GPU, API, payment or download is performed by the trainer. Checkpoints stay private.
5. This system cannot independently verify legal entitlement, license provenance or factual quality. Operators must not train on sources without applicable rights.

## Local CLI (Python 3.11–3.13, actual PyTorch required)

Install the optional neural worker:

```powershell
py -3.12 -m pip install -e ".[foundation]"
```

Find source IDs in the local database (the default Windows path is `%LOCALAPPDATA%\\NeuroGenesis\\experiences.sqlite3`):

```powershell
py -3.12 -m neurogenesis.knowledge_rights --db "C:\\private\\experiences.sqlite3" --list
```

Review content and rights independently, then approve **at least three separate source URLs** individually (replace IDs and path):

```powershell
py -3.12 -m neurogenesis.knowledge_rights --db "C:\\private\\experiences.sqlite3" --approve 1 --confirm-rights
py -3.12 -m neurogenesis.knowledge_rights --db "C:\\private\\experiences.sqlite3" --approve 2 --confirm-rights
py -3.12 -m neurogenesis.knowledge_rights --db "C:\\private\\experiences.sqlite3" --approve 3 --confirm-rights
```

Train a *candidate* on CPU, keeping the output in a private location (CUDA can be selected only on a machine with real supported CUDA):

```powershell
py -3.12 -m neurogenesis.knowledge_train --db "C:\\private\\experiences.sqlite3" --output "C:\\private\\foundation-candidate.pt" --confirm-corpus-rights --steps 20 --sequence 32 --device cpu
```

Revoke a source at any time: `--revoke 2`. Revocation prevents its inclusion in future training but **cannot make a previously saved checkpoint forget its gradients**. Treat old checkpoints accordingly; deleting one is an operator decision.

### Optional Command Center

Open `Wiedza`, select a retained source revision and choose **Zatwierdź prawa do treningu** or **Cofnij zgodę**. `Trening` has explicit rights confirmation, bounded step budget (1–1000), CPU/CUDA selection, real per-batch loss progress, cancellation and post-run measured holdout CE, Markov baseline, step/s and CUDA allocated bytes where CUDA is used. Saving a candidate does not replace chat or the user's spiking brain.

The Qt desktop is an optional separate application until Qt licensing and redistribution tests are complete; the existing Tk Windows EXE does not automatically gain this training panel.

## Guardrails and true evaluation

- Database remains schema=1 with additive `knowledge_rights_audit`; previous private brain, teaching, web events and source content are not reset.
- Only the **latest** explicitly approved revision per canonical URL can enter the corpus. Bounded to 64 source documents, 1 MiB aggregate data, and up to 6,000 extracted text characters per document. Repeated URL versions never leak into the training split as distinct documents.
- At least three distinct approved URLs. Stable source-URL ordering assigns one **whole document** to a held-out test set, with all others restricted to gradient training. No training window crosses document boundaries. This is more defensible than token-contiguous overlap, but it is **not an independent external audit collection** and may share language/patterns with train.
- Actual PyTorch multi-timescale GRU gradients train ordered next-byte prediction. Hard caps: 1000 optimizer steps, 8 samples/batch, 128 bytes/sequence, 256 hidden units, 1 MiB source corpus. Explicit `cpu` or `cuda` selection.
- Report actual held-out next-byte cross-entropy **before** and **after**, and compare with a Laplace-smoothed first-order **Markov byte baseline**, not a fake percentage of intelligence. Report actual training steps/s and peak allocated CUDA bytes only when the CUDA backend runs. An improved score is a measurement on the chosen holdout, not proven general language skill.
- Candidate checkpoint is written atomically after finite metrics, even when the measured improvement is negative (it is labeled *candidate* and never automatically deployed). Cancellation before checkpoint write aborts without promoting the model or touching the original SQLite.
- No automatic Internet access from trainer, use of remote compute, neural chat inference or run scheduling.

## Test gates

`tests/test_knowledge_training.py` checks local-only rights, audit/revocation/delete, latest-revision isolation, CLI permission refusal, numerical Markov baseline, real CPU Torch gradients, held-out metrics, checkpoint round-trip and cancellation. The dedicated Foundation CI job **installs real PyTorch CPU**; the standard dependency-free Python matrix skips only the Torch-specific tests while checking rights logic.

Required premerge: Python 3.11–3.13, real PyTorch CPU, Windows native/legacy frozen EXE, actual Qt Windows and Ubuntu, frozen Qt technical EXE and privacy CI. No verified CUDA performance can be claimed unless explicitly run on CUDA hardware.

## Next independent scientific gates

Natural held-out source corpora with verified permissions; document/domain splits and independent audit sets; calibrated source/fact quality and contradiction tracking; per-task evaluation of actual answers; retention and catastrophic-forgetting tests before any checkpoint promotion; matched Markov/GRU/Transformer comparisons at equal training compute; operator-controlled checkpoint rollback; GPU benchmarks on physical hardware. Do not present byte loss reduction as evidence of AGI or verified contextual reasoning.
