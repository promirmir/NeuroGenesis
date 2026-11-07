# NeuroGenesis — controlled Internet perception (v0.6.0)

**Official credit: Miron przy pomocy AI.**

## Windows interface

The Internet tab is OFF by default. Enable HTTPS access explicitly, enter a
public HTTPS URL without query/credentials, then click **Pobierz stronę i
przekaż mózgowi**. The app shows the actual URL, retrieval time, SHA-256
digest and limited plaintext extraction. The current private LIF/SQLite brain
receives extracted text as a hashed sensory observation. No website contents
are blindly executed, and no network connection starts at application launch.

Optionally enable refresh every **5 minutes** for the EXACT URL manually
approved previously. Editing the URL disables scheduled refreshing until
another explicit manual read. Disabling the checkbox prevents new reads;
turning HTTPS off before a worker finishes prevents storing its result.
Repeated identical page hashes do not create duplicate neural updates.

## Security controls

- HTTPS port 443 and public DNS hostnames only. No direct IPs, localhost,
  private network, credential-containing URLs, arbitrary ports or queries.
- Every resolved IP must be globally routable. DNS is checked ONCE, then
  the socket connects to one of the validated public IPs while TLS still
  verifies the original hostname and certificate. Mixed public/private DNS
  responses fail closed; DNS rebinding cannot redirect the actual socket
  into the internal network between resolution and connection.
- No redirects, cookies, login headers, automatic browsing, script
  execution, shell calls or external model downloads. A changed URL
  requires separate authorization.
- Only text/html or text/plain; uncompressed, up to 128 KiB of response
  bytes and 6,000 extracted characters. HTML parser ignores scripts,
  forms, headers and style blocks.
- Connection has six-second timeout. The request runs on a worker thread,
  while SQLite updates and Tk GUI changes occur on the UI thread.

This is a narrow, consent-based public-text sensor, NOT a general web agent.
Only one manually approved URL can auto-refresh. Respect individual websites'
terms and avoid high-frequency collection.

## Private state

The website can see the network egress IP. Its URL may reveal browsing habits
and is stored ONLY in the user's private SQLite database.

An additive web_observations table saves event ID, source URL, raw-body
SHA-256 and UTC retrieval time. It does not store the full page body.
Existing observations store hashed sensory data, source='internet' and a
neural brain snapshot. These writes share one SQLite IMMEDIATE transaction.
Identical URL/content pairs are deduplicated BEFORE further neural steps.
Deleting an observation also deletes its source record, but cannot
physically reverse synaptic changes already learned.

If input is invalid, the page is too large or private, a redirect occurs,
or the database is corrupted/full, the operation fails without resetting
the previously stored brain. The local SQLite DB is not encrypted.
Avoid entering secrets or private datasets; do not distribute its contents.

Offline CI mocks DNS/HTTP and verifies private IP/SSRF blocking, IP pinning
contract, redirects, size and content-type limits, extraction, atomic
provenance, deduplication, backward compatibility and deletion. The Windows
EXE self-test uses a synthetic local web event and never reaches a website.

## Scientific limits and roadmap

The fetched text currently reaches the old 8-channel hashed small LIF brain.
This does NOT constitute semantic understanding, critical evaluation or
humanlike intelligence. The new GPU-ready Foundation Brain is a separate
research path; integrating it with source-grounded language generation and
independent retrieval accuracy tests is required before making stronger
claims.

Next: verified permissioned data ingestion into a trained Foundation model,
source reputation, isolation with hard wall-time and resource limits, credible
cross-source factual grounding and operator-controlled knowledge retention.
Never execute a webpage's instructions or claim that provenance guarantees
factual correctness.
