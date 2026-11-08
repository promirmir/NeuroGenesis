# NeuroGenesis — public-web specialist discovery (PR #24 merged)

**Public credit: Miron przy pomocy AI.**

## What is actually implemented

- User enters a subject in the **Specjalizacja** tab of the native Windows
  Tk desktop and authorizes HTTPS in the existing **Internet** tab.
- The controller builds Wikipedia subject seeds, then follows extracted,
  relevant hyperlinks **across public HTTPS domains**. This is a bounded
  breadth-first crawler, rather than a hardcoded list of articles.
- Each source is downloaded as inert plain text/HTML, with TLS hostname
  verification and DNS/IP pinning. There are no redirects, scripts, cookies,
  login, query-string URLs, credential handling or remote code execution.
- robots.txt is fetched with the same secure public-only transport. Site
  restrictions and crawl-delay are honored; unverifiable rules **deny**
  autonomous retrieval. Robots 404 means no declared restrictions.
- Session budgets: operator selects **1–500 page attempts** (GUI defaults to
  120), 50 domains, at most 20 pages per domain, maximum link depth 3,
  600 queued candidates, and at least 5 seconds between page fetches.
  The site-specific robots crawl-delay may increase this gap.
- Each request is limited to 512 KiB for this explicit crawler mode;
  pre-existing manual HTTPS perception stays capped at 128 KiB. Extracted
  observation text is capped at 6,000 characters, candidate links at 256.
- Successful observations pass through existing
  \`ExperienceMemory.observe_web\`, retaining source URL, timestamp, SHA-256
  and atomic local neural-state transaction. No raw full-page HTML is saved.
- UI shows progress, attempted/saved/error counts, discovered URLs and domain
  count, and provides Stop. Revoking HTTPS consent stops future acquisition.
  SQLite writes are dispatched from worker requests to the GUI thread.
- Tests use only mock connections and fake robots content. CI never crawls the
  real web.

## Important limits

This does **not** scan the entire Internet. It traverses only relevant
public hyperlinks reachable from its topic seeds and is constrained by
robots.txt, site restrictions, budgets, query-less HTTPS URLs and network
availability. Some pages, forums and documents will not be reachable; HTML
larger than 512 KiB, JavaScript-only pages, PDFs and redirects are rejected.
There is no external search index or search API and no guarantee of coverage.
The operator's public IP and requested page URLs are visible to websites.

Data acquisition and an update to the original small spiking sensory pathway
are **not** proof of factual accuracy, specialization or learned language
understanding. This feature does not train weights of the separate optional
PyTorch Foundation Brain, does not certify expertise and does not carry out
instructions discovered on external pages.

## Acceptance / release state

PR #24 has been squash-merged to main SHA `578222800c5adc73c0a756352b5bef405535252a` after green Python 3.11–3.13, privacy and Windows standalone EXE checks. Main-branch Linux/Windows validation and release workflow succeeded. Verified Windows download is release `v0.6.0-main.57822280`, containing `NeuroGenesis.exe` and its SHA-256. The crawler's actual effectiveness on public websites is **not** independently established by CI. The optional PyTorch Foundation Brain is unaffected and still not trained on these pages.

Relevant code: \`neurogenesis/specialist_study.py\`,
\`neurogenesis/web_discovery.py\`, \`neurogenesis/web_sense.py\`,
\`neurogenesis/study_panel.py\`. Tests:
\`tests/test_specialist_study.py\`, \`tests/test_web_discovery.py\`,
\`tests/test_web_sense.py\`.
