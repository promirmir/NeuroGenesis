# Specialist study — first bounded backend candidate

**Miron przy pomocy AI.**

This branch introduces `neurogenesis.specialist_study`, an explicitly authorized
and interruptible sequential source-acquisition controller. The operator supplies
a topic and gives consent before `run(consent=True)`; no network call occurs
during construction. The current seed planner derives up to 20 public Polish
Wikipedia article URLs, each validated by the existing HTTPS/SSRF gate.
It is deliberately **not** an unrestricted search engine or crawler.

Each successful source observation can be handed to
`ExperienceMemory.observe_web`, preserving the existing SQLite provenance
transaction. The controller itself never stores raw downloaded page text.
Requests are sequential with a minimum 5-second delay; errors are counted
without exposing page content. `stop()` interrupts between requests.

## Limitations and acceptance

- This is **not** model weight training, semantic understanding, specialist
  certification, forum discovery, or broad web search.
- A topic may map to a nonexistent Wikipedia page; failures are reported.
- The Windows Tk desktop now includes a separate Specjalizacja tab with topic input, start/stop, progress and URL log. It shares the Internet tab's explicit HTTPS consent. SQLite writes are dispatched to the GUI thread.
- Network behavior remains opt-in and must not run in CI. No GPU claimed.
- Validate Python 3.11–3.13, privacy checks and Windows frozen EXE before merge.
- Candidate source commits: `b7520d851b97a81dfcb6df1c1cdc1aa969a453ca`
  and `b04a4c05b76a63bdb0c807cb8a2e647639959e0e`.
- CI status at creation: **not yet verified**; do not merge until gates pass.
