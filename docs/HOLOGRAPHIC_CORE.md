# Holographic Neural Core — real-data 3D-like monitor

**Status: implementation candidate, not yet a published binary.**
The public Windows `NeuroGenesis.exe` remains the previously verified
`v0.8.0-main.8e27f420` until this branch is merged, Windows CI completes and
a new source-SHA-bound release is independently confirmed.

## What the user will see in the actual Tk application

- The initial `CENTRUM` page now defaults to a continuously orbiting,
  brain-shaped **symbolic 3D projection** of the *actual saved LIF neurons*.
- Lines correspond only to the actual saved synapses and their weights.
- A brief bright edge wave appears only after **a newly recorded LIF step**
  with a fired source neuron. The temporal wave is an illustrative
  visualization; it does **not** measure biological propagation delay.
- The camera rotates even when the brain is idle; **camera rotation is not
  neural activity**. It can be paused. No periodic memory writes, fake training
  score, fake GPU measurements or background network requests occur.
- A button switches back to the existing exact 2D connectome without losing
  the previous renderer, stored memory or controls. Both share the same
  `snapshot_neural_telemetry(ExperienceMemory.brain())` source.
- Drawing caps: **144 visible nodes and 360 visible edges**, 90 ms/frame
  while the widget is visible. The footer marks truncated views. The
  semantic labels explicitly distinguish ornamental position/camera from
  the real event stream.

The view **is not** a scanned human brain, a physical AI avatar, a map
of PyTorch GRU weights or proof of general reasoning. Neural placement is
deterministic but symbolic; this project has no true anatomical mapping.

## Actual compute capacity change

For **new** SQLite memories only, default LIF resource ceilings rise from:

| Resource | Original defaults | New defaults |
|---|---:|---:|
| Maximum LIF neurons | 128 | 512 |
| Maximum synapses | 1024 | 4096 |
| Pattern store | 256 | 1024 |

These are maximum limits, **not immediately allocated neurons or increased
processing speed**. Initial neurons stay 24 and the network still grows in
response to new stimuli under its existing plasticity rules. Every saved
brain snapshot includes the full original `BrainConfig`; loading a database
with 128/1024/256 retains those limits unchanged. The status line displays
the actual active per-database limits, not the new defaults.

The separate Foundation Brain is already operator-configurable and
requires controlled local, rights-cleared training; this branch does not
silently increase GRU weights, training resource usage or GPU consumption.
Increasing raw LIF neuron counts alone cannot establish language
understanding or an AGI capability gain.

## Required acceptance before calling this released

1. Headless deterministic projection / idle-event / saved-spike / old-config
   regression tests on Python 3.11–3.13.
2. Real Windows Tk GUI test with both 3D/2D views and synthetic disposable
   SQLite; frozen `NeuroGenesis.exe --self-test` and `--ui-self-test`.
3. Existing Qt Windows/Ubuntu, privacy tests, separate PyTorch CPU test and
   default Windows packaging must remain green.
4. Inspect new Windows synthetic-data screenshot; rotation should remain
   readable at lower resolutions and without a GPU dependency.
5. Only after merge+CI confirm the *new* public EXE exact tag, byte-size,
   SHA-256 and source commit. A source PR is NOT an installable release.

No autonomous web crawling, new consent model, private data reset or cloud
dependencies are added by this feature.
