# Security model

## Current v0.6.0 candidate attack surface

- The existing CPU neural/SQLite core and Foundation Brain experimental worker remain local. Internet tab introduces **optional, operator-enabled** read-only HTTPS perception; there is no auto network connection at startup.
- Only public DNS HTTPS:443 URLs with no query/userinfo. DNS is resolved once, all IPs checked as global and the TLS socket connects to the verified IP while authenticating the hostname. Deny redirects, IP literals, local/private IP, compressed/binary downloads and code execution. Body capped at 128 KiB, extracted text at 6,000 characters.
- A worker fetches inert text, the UI commits source URL/UTC/SHA-256 and neural hashed features in one SQLite transaction. Duplicate content is ignored. Full raw page content is not stored. Website sees the user's public IP.
- Opt-in scheduled refresh checks only the last manually approved URL every 5 minutes; if HTTPS is switched off, fetched content is not stored. No JavaScript; the specialist crawler is separately authorized and bounded, as described below.
- Existing risks remain: URL/source metadata may be sensitive, local database unencrypted, full page text may be incomplete or inaccurate, six-second socket timeout is not a strict total request time budget. Do not treat network content as a command or independently verified fact.

## PR #24 candidate: opt-in cross-domain source discovery

The new specialist tab does not run by default. After explicit HTTPS consent, it follows only topic-related extracted HTML links from public Wikipedia subject seeds, including links to other public domains. It validates every candidate with the existing query-free HTTPS:443, public-DNS/IP-pinned TLS reader; denies private IPs, redirects, scripts and arbitrary HTTP methods. robots.txt requests also use pinned TLS, deny inaccessible or redirecting policy files, and honor disallow and crawl-delay. The crawler has upper bounds of 500 attempted URLs, 50 domains, 20 pages/domain, link depth 3, candidate queue 600 and >=5 seconds between page fetches. The manual reader remains limited to 128 KiB; explicit crawler reads are limited to 512 KiB; extracted text is capped at 6,000 characters. Topic text becomes part of requested public Wikipedia URL paths and is visible to destination servers; do not enter secrets. Page content is inert and cannot authorize commands.

Limitations: robots.txt is only one layer of access policy; site terms and rate limits still apply. There is no site login, full web search API, query URL support, JS rendering, PDF processing, authenticated access or actual model-weight training. Real-site compatibility has not been proven by offline GitHub Actions. Additional resource and cancellation hardening is required before unlimited crawling. No unbounded scanning is authorized.

## Historical v0.5.4 offline attack surface

- All commands in the v0.5.4 baseline were local and offline. No network permissions, crawling, arbitrary shell execution or automatic code modifications existed.
- `observe` treats text as inert sensory data; it does **not** interpret instructions within it. It has no semantic understanding.
- Brain and predictor state snapshots are versioned JSON, **not executable pickle**. Loads reject overlarge files, wrong schema, non-finite values, invalid graph indices and invalid dimensions. Snapshots are not encrypted.
- The public repository must contain **no secrets, API keys, authentication tokens, personal datasets or conversation logs**.
- State files should be stored outside the repository or match the `.gitignore` rules; when shared, consider them potentially sensitive.

## Further hardening needed before broad autonomous internet research

Implement all of: explicit user opt-in, read-only allowlists, domain and IP validation against SSRF, redirect re-validation, per-request size and time limits, MIME and charset handling, rate and crawl budgets, privacy boundaries, source attribution, injection-resistant separation of retrieved content from instructions, and logging/disable controls.

## Before enabling autonomous code changes

Require sandbox execution, restricted capabilities, independent test gates, resource quotas, reproducible comparisons, rollback, signed artifact provenance, and explicit human approval for deployment. **Do not let untrusted pages or model output directly execute commands or modify production source.**

## Vulnerability reporting

Avoid posting exploit details and secrets in public issues. Contact repository maintainers through an agreed private reporting channel if one is published. No private reporting endpoint is asserted to exist yet.

## Public source and Git metadata gate

Source files and commit **display names** are scanned for identifying content by `python -m scripts.privacy_audit --git`. The operator explicitly accepted Git author email visibility; no private surnames are permitted in author/committer names or tracked source, and credentials, local user paths and private observations must never be published. Independently inspect new Git commit author/committer names and verify CI before merge. Do not run legacy fresh-root publishing tools or rewrite active history. A source clean-up cannot erase old commit objects or external copies.

## Local SQLite experiences (v0.4)

Memory databases are local files; their names are ignored by Git, but this is
not encryption. The default storage retains hashed features and unsalted
SHA-256 text fingerprints, which may leak guesses about short/low-entropy
inputs if someone obtains the DB. The `--store-text` option explicitly stores
plaintext and should not be used for sensitive data. Transactions commit brain
state and record together. `forget-event` deletes a record but not learned
weights; to remove all stored evidence, securely discard the entire local DB,
not merely the corresponding event. Protect filesystem/backup access.
