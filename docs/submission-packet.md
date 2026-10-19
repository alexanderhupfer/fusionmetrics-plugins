# Fusionmetrics submission packet

Updated 19 October 2026 for version 0.2.5. This document records proposed listing answers, verified tests, publisher approvals and the remaining publication gates. Evidence is scoped to the checks described; it does not certify directory acceptance. Keep reviewer passwords, private account identifiers, OAuth tokens, and unredacted recordings outside this public repository.

## Listing fields

| Field | Value |
| --- | --- |
| Name | Fusionmetrics |
| Short description | Shopify analytics and growth |
| Publisher | Fusionmetrics / AC App-Commerce UG (haftungsbeschränkt) |
| Contact | Alex from Fusionmetrics, Founder — alex@fusionmetrics.com |
| Website | https://fusionmetrics.com/agent-setup |
| Support | https://fusionmetrics.com/support/chat |
| Privacy | https://fusionmetrics.com/privacy |
| Service terms | https://fusionmetrics.com/terms — deployed page verified on 18 October 2026 |
| MCP endpoint / OAuth resource | https://fusionmetrics.com/api/mcp |
| Repository | https://github.com/alexanderhupfer/fusionmetrics-plugins |
| Claude plugin path | plugins/fusionmetrics |
| Release branch | main, after the compatible service is deployed and client tests pass |
| License | MIT for plugin files; hosted service terms apply separately |
| Category | Productivity |

Long description:

> Analyze Shopify app revenue, MRR, churn, trials, Merchant activity, and available acquisition data with Fusionmetrics. Use the same read-only analytics tools as the existing MCP connection, including available contacts and reviews. Improve Shopify App Store listings with evidence and approved browser edits. Set up revenue imports and GA4/BigQuery acquisition data, validate a dataset connection, and track its import. Sign in to Fusionmetrics in the browser and select your Organization. A Fusionmetrics account and eligible plan are required; configuration writes require an Organization administrator. Google administration and Shopify listing edits use your separately authorized browser session. Optional contact capture supports Shopify's official React Router app template and requires local repository access and a separate deployment. Existing MCP connections remain supported during migration.

Suggested prompts:

- Explain my app's revenue and MRR changes.
- Recommend improvements to my Shopify App Store listing.
- Help me set up GA4 and BigQuery for my app.

Platform scope: the prepared Claude listing is explicitly limited to Claude Code. Cowork and Claude apps (web, desktop, mobile) are unchecked; the separate custom connector remains a validation surface. Validate Codex desktop and Claude Code separately. Browser-dependent workflows require an authorized browser integration available in that client. Do not claim that installing this package supplies browser control, Google/Shopify credentials, a mobile experience, or a custom MCP UI. No MCP UI screenshots are needed unless an actual UI resource is added.

## OAuth and native-client checks

Use DCR with PKCE through the endpoint's authorization-server discovery. The requested scopes are `openid user:org:read setup:read setup:write analytics:read`; the resource is exactly `https://fusionmetrics.com/api/mcp`. Do not embed client secrets, bearer tokens, Partner account credentials, or Google keys in the package.

On 18 October 2026, the production Fusionmetrics Clerk application was configured with the advertised custom scope `analytics:read` and explicit consent text covering prepared revenue, MRR, acquisition, Merchant contacts, and App Store reviews. Public authorization-server discovery advertises all five requested scopes. Native Codex DCR and Claude Code CIMD grants were verified with the dedicated reviewer. The generic `/api/mcp` authorization challenge must also request all five so clients that use it discover analytics. Existing setup-only grants remain supported. Adding a scope is not evidence that an old grant has it: test fresh authorization and reauthorization in each client. Use the isolated review Organization for publication tests.

The OpenAI ZIP embeds the documented auth extension. Repository/native manifests intentionally remain compatible with current clients; Claude pins scopes in `.claude-mcp.json`. Portal validation and actual native Codex consent remain required because the published portable MCP schema and current CLI disagree with the OpenAI extension. Do not fix this by broadening default permissions for unrelated clients.

## Tool annotations and justifications

These describe the candidate server. Compare every row with the live tool scan after deployment. R = read-only, D = destructive/replaces existing data, O = accesses external systems. All tools declare idempotency; setup writes require a stable operation key, which must be reused after an uncertain response.

| Tool / title | R | D | O | Justification |
| --- | --- | --- | --- | --- |
| `list_apps` — List apps | true | false | false | Reads authorized apps with prepared artifacts; does not modify business data or call Shopify. |
| `select_app` — Select an analytics app | true | false | false | Changes only session selection and an in-memory database; no persistent business mutation. |
| `describe_schema` — Describe analytics schema | true | false | false | Reads prepared table definitions and metric guidance in the selected Organization. |
| `run_sql` — Query prepared analytics | true | false | false | Bounded read-only SQL over prepared analytics; filesystem reads and mutations are rejected. |
| `setup_get_instructions` — Read setup instructions | true | false | false | Returns versioned workflow instructions. |
| `setup_get_status` — Check setup status | true | false | false | Reads Organization setup/import state; excludes credential values. |
| `setup_request_credential_entry` — Open secure credential entry | false | false | false | Creates an expiring browser handoff; the human enters secrets separately. |
| `setup_discover_apps` — Discover Shopify apps | false | false | true | Queues discovery/import using the connected Partner account and Shopify API. |
| `setup_configure_app` — Configure app imports | false | true | true | Can replace app display/billing configuration and queue an import after human confirmation. |
| `setup_retry_import` — Retry an import | false | false | true | Retries an eligible failed job; earnings imports can call Shopify. |
| `setup_get_capture_installation` — Prepare contact capture | false | false | false | Reserves an app-specific capture identity and returns a public snippet; does not deploy it. |
| `setup_mark_capture_prepared` — Record local capture preparation | false | true | false | Updates the stored preparation state; does not assert deployment or a live receipt. |
| `ga4_get_status` — Check GA4 and BigQuery connections | true | false | false | Reads saved mappings, public service-account identity, and scoped import state; no event queries or keys. |
| `ga4_configure_dataset` — Validate and save a GA4 dataset | false | true | true | Calls BigQuery validation and can replace an existing mapping; failed validation preserves the old mapping. |
| `ga4_import_attribution` — Import GA4 attribution | false | false | true | Queues a validated dataset import; the worker reads BigQuery and publishes derived acquisition artifacts. |

Required permissions: the first four tools require `analytics:read`; read-only setup/GA4 tools require `setup:read`; setup/GA4 mutations require `setup:write`, current Organization administrator membership, and the applicable plan entitlement. Session identity, organization, grant, and role must remain valid. The plugin does not administer Google IAM or Shopify listings through MCP; those are separate authorized browser actions.

## Proposed data-handling answers

- Data processed: selected Organization/app metadata, prepared revenue and subscription metrics, Merchant records, available captured/imported contact details, review text, GA4 acquisition reports, setup state, and public credential identities. Results depend on granted scopes and the requested tool.
- Assistant disclosure: requested tool results are sent to the connected assistant provider. Do not describe the entire integration as anonymous or free of personal data. Contacts and reviews may contain personal data.
- Credentials: human-only browser forms collect Shopify Partner API tokens, Shopify Client Secrets, and optional Google credential material. Public plugin files and normal tool responses do not contain their values. Google and Shopify sessions are separately authorized.
- Writes: the service can save setup/configuration state, create credential handoffs, and queue imports. Listing publication and Google administration require separate authorization in the browser. Local contact-capture changes are not automatically committed or deployed.
- Storage: the hosted service stores scoped application state and prepared analytics. Setup-operation results are retained for retry deduplication. Tool telemetry records tool name, duration, outcome, and a hashed client identifier. Do not claim zero retention or zero telemetry.
- Deletion/revocation: disconnecting removes the assistant connection. Revoking the OAuth grant prevents refresh, but Clerk access JWTs already issued can remain usable until expiry, currently up to 24 hours. Current Organization membership is checked on every request. Neither action recalls assistant messages or deletes service records. Use the privacy policy and support process for deletion requests. Verify current retention and subprocessor disclosures before attesting to them.
- Charging: no purchase is made by an analytics tool. An eligible Fusionmetrics plan is required; do not claim that the hosted service is free because the plugin files use MIT.
- AI training, regional storage, contractual processing terms, certifications, and exact retention periods: answer only from approved company policy. The code audit does not establish these claims. Leave unsupported portal answers unconfirmed.

The package declares an optional bundled Python validator, user-authorized local app edits/checks, and separately authorized browser workflows. The validator reads local JSON reports and makes no network calls. Capture setup asks the host to run the app repository's type/build checks. There are no installation hooks or background executables. These local commands run through the assistant host's normal tools; analytics and setup service operations use the declared Fusionmetrics MCP server. The setup workflow and template recipe are bundled, avoiding dynamically fetched behavioral instructions.

On 19 October 2026, the publisher approved proceeding with this disclosed behavior after reviewing [Anthropic's documented support for bundled skill scripts](https://code.claude.com/docs/en/skills#generate-visual-output) and the [Directory Policy's allowance for user-intended external tools](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy). All six OpenAI declarations are checked in its prepared dialog. Claude shows all four compliance acknowledgments saved and its final review page available, with automatic publication disabled. This is the publisher's approval based on the disclosed host execution, not an Anthropic ruling on the form's wording or an acceptance decision. Both directory submissions remain drafts.

## Reviewer account and test data

Reuse the existing iPhone App Review account and its dedicated fictional production Organization for both plugin reviews, live tests, and the demo, as requested by the publisher on 18 October 2026. The private iPhone review record documents two populated Apps, dashboards, reviews, Merchant history, an explicit lifetime access grant, and successful password-only sign-in. Keep the account identity and its existing password in 1Password and the portals' protected reviewer fields, outside this repository and ZIP. No new primary reviewer account or Organization is needed.

Recheck that the account remains restricted to the fictional Organization, its access grant covers setup and analytics, and its role permits the configuration cases. Verify a fresh browser OAuth sign-in without founder-supplied email codes or MFA in each intended client; the previous iPhone sign-in is not evidence of plugin OAuth scopes or compatibility. Preserve the existing password, account-scoped sign-in configuration, and iPhone review baseline. Supply the same credentials privately when preparing the plugin reviewer fields.

The 18 October production read-only audit confirmed an active Organization, exactly one administrator member, the existing lifetime access grant, password authentication without MFA, and no membership in other Organizations. Both individual App dashboards and the aggregate exist. The Sprout Reviews fixture loads through the analytics engine and contains 30 range-metric rows, 30 revenue rows, three Merchant summaries and six Merchant timeline entries. Its fixed sample period is 30 August–28 September 2026; these are not current live metrics. At the initial audit the Organization had no Shopify Partner profile or scheduled revenue refresh. It now includes a separate test-only Shopify Partner account, development store and App. Actual discovery, app configuration and import completed successfully; the original synthetic revenue Apps remain unchanged. The test App has zero earnings, as expected. Use the individual Sprout Reviews and Beacon Bundles fixtures for fixed revenue examples: the current All apps dashboard shows zero after the test import and is not a reconciliation of those samples. A final direct Sprout query still returned MRR 8,240 for 28 September. No real Audience-Push data is connected. A managed BigQuery credential and synthetic Sprout dataset were subsequently connected through normal product controls. The GA4 import completed, and prepared data contains 20 listing views, six add-app clicks and four installs for September 27–28. These tables were generated for importer testing. Separately, a real isolated GA4 property and web stream now receive browser page views and a named review event. The native daily BigQuery export link was created on 19 October; its first table/import and Shopify listing tracking remain pending. Both native clients authenticated normally. The test App’s capture credential was entered through the secure browser form, and its public snippet was integrated once into a local copy of Shopify’s official React Router template. Typecheck and production build passed. The isolated test App now opens a separate deployed staging App Bridge harness using the published capture snippet. Normal MCP status verified contact_received with a usable contact at 19:40:21 UTC. This live harness test is separate from the local official-template build check; it does not claim that the full official template was deployed. Raw audit records and credentials remain private.

Use a separate non-admin test identity in the same isolated Organization for permission tests, and a second isolated Organization for cross-Organization denial tests. These are negative-test fixtures, not replacement primary reviewer accounts. Revoke only the plugin test grant during revocation tests; preserve the iPhone review identity and its access. Do not create a real Stripe charge or disable authentication or membership enforcement globally.

### Reviewer access and publisher testing

Reviewers sign in to the existing populated Fusionmetrics account. The five packaged positive cases inspect setup status, prepared MRR, fictional Merchant activity, a supplied listing-copy draft and GA4 readiness. They require no Shopify Partner login or Google administrator account. Seeded analytics are real prepared artifacts served through normal authentication and analytics tools; describe them as synthetic sample data with a fixed date range.

Shopify Partner access belongs to the publisher's integration tests. An existing publisher-controlled Partner account can be used when the exact App and operation are authorized; creating a separate Partner account is not inherently required. Keep that access and any real Partner data outside the shared review Organization. OpenAI’s reviewer form explicitly requires sample data only. Audience-Push is therefore a private publisher test resource; sharing its production records is not the reviewer solution. A separate test-only Partner account and sample development store were created with publisher authorization. Its API client is connected through the normal secure setup flow, and its test App has a completed import. Reviewers can exercise connected-account discovery/configuration without an unrelated production Partner login. The test App’s listing editor remains gated by Shopify App Store registration; no registration payment or public listing submission was performed. Listing recommendations can be evaluated from supplied copy and available analytics; an admin-authoritative baseline is required only when testing actual listing changes. Status inspection and setup guidance must accurately report missing connections rather than imply an import ran.

This review design does not waive functional coverage. [OpenAI requires a ready-to-use test account and executed review cases](https://developers.openai.com/plugins/deploy/submission); [Anthropic requires testing every exposed tool and providing a populated account](https://claude.com/docs/connectors/building/review-criteria). The selected eight cases do not exercise every write tool. Before submission, resolve how reviewers can evaluate the remaining declared operations using safe, authorized resources, or obtain a documented platform decision on disclosed access limitations. A recording or mocked provider response is not evidence that a reviewer can successfully run an unavailable tool. Keep those readiness gates pending.

Preserve the two iPhone review Apps and their existing baseline. Inventory these reviewer resources through the normal supported data pipeline:

| Resource | Required state and expected evidence |
| --- | --- |
| Existing revenue demo | Sprout Reviews' fixed 30 August–28 September 2026 MRR series closes at USD 8,240. Its three Merchant summaries and six timeline rows are independently audited. Report unavailable movements/cohorts as unavailable. |
| Listing draft | The prompt supplies fictional copy and its feature claim. Assess clarity and factual accuracy; acquisition performance remains unmeasured until suitable prepared data exists. No Partner Admin login or listing edit is part of this case. |
| Setup and GA4 status | Report the saved managed credential and completed synthetic Sprout import. A real isolated property and web stream have received browser events; the native daily export link is created, while first-table/import verification and Shopify listing tracking remain pending. Beacon has no GA4 mapping. Do not connect real Partner data merely to make the sample appear complete. |
| Negative cases | Requests for unauthorized Organization data, credential disclosure and analytics SQL writes must be refused or rejected without changing the sample data. |

Publisher testing remains broader than these review cases:

| Resource | Required state and expected evidence |
| --- | --- |
| Revenue coverage | Separate synthetic fixtures for MRR movements, churn, trials and cohorts, with an independent reconciliation ledger and recorded parity results. |
| Shopify integration | An explicitly authorized App under publisher-controlled Partner access for discovery, configuration and completed imports. Listing edit tests require a separately authorized exact target/change and restoration for temporary experiments. Keep real credentials and data out of the shared reviewer account. |
| Acquisition import | Synthetic daily BigQuery tables and narrow managed access can exercise mapping and completed imports without Shopify Partner login. They do not prove a real GA4 export or Shopify tracking configuration. Test that provider setup separately when authorized access is available. |
| Contacts/reviews and failures | Fictional contacts/reviews, embedded untrusted instructions, missing tables, denied dataset access, failed imports, read-only membership, setup-only grants and cross-Organization denial. Use isolated resources and preserve the valid baseline. |
| Capture app | A local official Shopify React Router template with reproducible checks. Record local changes separately from a deployed capture receipt. |

If a publisher resource is unavailable, record the affected case as blocked. Keep analytics and copy-review preparation moving, but do not treat sample artifacts, mocked tests or recorded demonstrations as successful live Shopify execution. The broader scenarios remain in [extended-test-cases.json](./extended-test-cases.json), outside the installable plugin and OpenAI ZIP.

## Current live setup evidence — 18 October 2026

The final hosted revision is `5d253cac4e3c0e666ec5989ed2355580dcc843ce`, deployed through the normal main CI/CD workflow. Health, the exact OpenAI domain challenge, all five challenge scopes and public terms/privacy responses passed verification. OpenAI now shows the MCP as configured, authorized and domain verified. Its rescan retains only a human-review finding for the credential-handoff tool. Fresh Claude web authorization and its connector draft both expose all 15 tools.

The isolated test Partner account completed real app discovery, configuration and import. The ready App and exact Client ID were verified. Repeating the same configuration reused the ready result without another import. Capture preparation used the app-specific public snippet in official template revision `48b841a7746e1b08d1e6d8793b1208f3096e41d0`; actual installed-template TypeScript and build checks passed. Shopify’s isolated snippet validator could not resolve the official framework modules, so it is not counted as a passing check. Local preparation and its idempotent replay succeeded; the later deployed harness receipt is recorded below. Calling retry on the completed import returned an actionable 409 and left the run unchanged. A later isolated worker interruption produced a real failed app-preparation run; the normal MCP retry completed successfully, returned the App to ready, and preserved the Sprout MRR sample at USD 8,240. Replaying its idempotency key returned the same execution without another job. No stored credential or job status was edited to manufacture the failure.

Actual Claude web custom-connector execution exercised all 15 exposed tools with per-call approvals: 14 returned successful results, and retrying the original completed import returned the expected 409. The Claude-initiated Shopify import completed at 18:14:28 UTC; its synthetic GA4 import completed at 18:09:20 UTC. During that earlier assistant run, the test App was ready and capture was locally prepared without a receipt; the later live harness check succeeded. The read-only session also exercised app selection, schema inspection and SQL. Assistant inferences about partial-day freshness or currency units are not certified by this tool-execution record.

The live non-admin boundary also passed: a temporary member completed normal password and new-device verification, authorized all five scopes, read status and analytics, and received HTTP 403 “Organization admin access required.” from all eight write tools. The temporary grant was revoked and identity removed; the original reviewer remains the sole administrator.

The live capture check used an isolated embedded Shopify App Bridge page on staging revision `86fcf6d05f0efe6d8fdc8bc1ba3230f872288598`, deployed through [application PR #156](https://github.com/alexanderhupfer/fusionmetrics_v3/pull/156) and the normal staging CI workflow. Opening the installed development-store app produced a real signed-token exchange and server receipt: normal MCP status returned `contact_received`, `usableContact: true`, and receipt time 19:40:21 UTC. No contact value is published here. Nine focused checks and the full CI/staging workflow passed. The application PR remains unmerged; production remains at the revision above.

An isolated GA4 property and web stream have now been created. GA4 Realtime verified one real page_view and one fusionmetrics_review_visit from a separate staging page, plus the standard first_visit and session_start events. This proves browser collection, not Shopify listing or install traffic. On 19 October, the native daily BigQuery export link was created in the approved US location with only the isolated stream selected; streaming, advertising identifiers and separate user-data export are disabled. A fresh post-link visit also reached GA4 Realtime. Google has not yet created the export dataset or first daily table, so native-table validation and the normal Fusionmetrics import remain pending. The existing managed connection already has access in this project; no manual IAM grant was added. The synthetic Sprout mapping remains unchanged. The isolated GA4 Measurement ID was saved in the English listing draft and verified after reloading; no Measurement Protocol secret is configured, and live listing/install traffic remains unverified. The isolated Partner account is now registered, with its associated-account declaration confirmed by the publisher. In its English listing draft, the subtitle was saved, verified after reloading, restored to its original empty value and verified again. Shopify displayed listing-completeness warnings while still persisting the draft changes. The App remains unpublished: public rendering, public restoration and ranking effects cannot be verified with this resource. This is an explicit coverage limit, not a passed live experiment. Actual failed-import recovery passed separately as described above. Publisher acknowledgments are complete as recorded above; final submission remains unperformed. No production Partner records were added to the shared reviewer Organization.

## Live execution record

The proposed prompts and expected outcomes in `plugins/fusionmetrics/plugin.json` under `extensions.com.openai.review.test_cases` contain exactly five positive and three negative cases, matching the OpenAI initial-review contract. Execute those eight cases using the existing reviewer identity and candidate package. Execute the separate publisher scenarios with their declared prerequisites and record their evidence separately. None is complete merely because its prompt is written. Record privately:

| Field | What to capture |
| --- | --- |
| Revision | Plugin commit, ZIP SHA-256, deployed service SHA, client name/version, UTC time |
| Authorization | Selected Organization, consent scopes, fresh vs upgraded grant; redact tokens and personal identifiers |
| Test | Exact prompt, relevant tool names, actual output, expected result, pass/fail/blocked |
| Writes | Confirmed exact target/diff, actual saved state, job ID/status, cleanup/restore evidence |
| Failures | Scope/admin/cross-Organization denial, revocation, missing data, rate-limit handling and retry behavior |
| Parity | Same app, artifact generation, SQL and row limit on legacy analytics and plugin; compare result data and metric definitions |

Add fresh install, reconnect, revocation and interrupted retry to the publisher execution record, not to the OpenAI case arrays. For actual listing changes, separately verify an approved permanent edit and a temporary experiment with restoration. For GA4 imports, record completion and prepared-data availability; a successful validation or queued job alone is insufficient. The package contains workflows, not proof that the platform's browser integration performed them.

## Demo recording plan

### Recorded walkthroughs — 18 October 2026

- [Codex CLI walkthrough, 4m22s](https://drive.google.com/file/d/1Hq9_Ov-tK8naDcTdz0NJMe32DJ3mUkOq/view)
- [Claude Code walkthrough, 2m42s](https://drive.google.com/file/d/1U6JQrNfyibsgRnvQIidxe3CwL_uDzHLQ/view)

Both videos show actual client sessions with the preinstalled 0.2.4 candidate, normal reviewer OAuth, and fictional data. Each demonstrates all five positive and three negative cases. Candidate 0.2.5 adds review metadata; the five skills and MCP configurations are byte-identical to the recorded version. Only idle pauses and bootstrap/exit were removed. The videos do not demonstrate desktop GUI installation, Shopify discovery, live Google provider setup, or contact-capture deployment. Browser preview processing can lag after upload; the files are also downloadable. Both files have reader access for anyone with the link, and their uploaded sizes and MD5 checksums match the reviewed local MP4s.

The original capture plan below identifies additional scenes that are not in these core-case walkthroughs. Keep those distinctions in reviewer instructions.

Record the actual supported client experience with synthetic data, normally at 1920×1080. Use the existing Chrome profile/approved browser connection; do not launch an automation profile. Do not display secrets, tokens, real Merchant contacts, or private account lists. Pause capture during sensitive sign-in. Clearly label cuts over actual export/import waiting.

| Scene | Visible evidence |
| --- | --- |
| 1. Install and connect | Plugin identity/version, browser sign-in, Organization selection, and enabled capabilities; no terminal installation commands. |
| 2. Revenue question | App selection, bounded analytics tools, period/freshness, and totals that match the independent synthetic ledger. |
| 3. Listing recommendation | Supplied fictional draft, available evidence, exact proposed wording and explicit traffic limitations. No Partner Admin access or saved/public-state claim. |
| 4. GA4 readiness | Actual connection status and next browser steps. Explain what requires the Partner's Google/Shopify authorization without claiming setup has completed. |
| 5. Failure boundary | The packaged unauthorized-access, credential and SQL-write cases, with accurate refusal/rejection and unchanged sample data. |
| 6. Optional capture | Local official-template preparation and check result; distinguish it from deployment. |

Show both intended clients, or supply separately labelled recordings. Capture the fictional Merchant-summary case as well as MRR so every packaged positive case is demonstrated. Supplement these reviewer scenes with publisher-controlled footage of actual setup/import and authorized listing edits when those tests are complete. Identify that footage and its external-account prerequisites explicitly; it does not replace tool access for reviewers. Review the final encoded video and contact sheet. Upload only the redacted final recording to a reviewer-accessible location; put its actual URL in `review.demo_recording_url`. A storyboard, screenshot montage, or synthetic UI is not a live demo.

## Portal sequence and release handoff

1. Release the compatible service via its normal CI/CD: feature-branch staging validation, approved merge to main, production workflow, exact deployed-SHA check. Publish the approved terms/privacy changes with it. No direct VPS deployment.
2. Configure/verify Clerk's advertised analytics scope and actual client grants. Run `scripts/probe_public.py` for public metadata; retain the report outside the repo. Fix Cloudflare/scanner failures by testing the actual portal scanner, not by assuming a shell probe proves reachability.
3. Build the OpenAI ZIP. Upload as a draft under the intended verified business identity; inspect advanced OAuth from the package. Complete the exact domain challenge supplied by the portal at `/.well-known/openai-apps-challenge`. The portal-issued challenge is in application PR #154; verify its deployed response before using the portal verification button.
4. Scan tools and compare all 15 titles/annotations with the matrix. Attach reviewer credentials privately, the test evidence, and the real video. Leave legal/compliance attestations for the publisher.
5. In Claude's publisher portal, validate the repository/path/exact revision. The Claude Code-only plugin uses its bundled remote MCP configuration. The separate custom-connector draft is available for validation; broader Cowork/Claude-app availability requires completing the applicable connector publication and pairing steps. Validate again after moving from a candidate branch to main.
6. Mark readiness gates verified only with current evidence. Run `python3 scripts/validate.py --submission-ready` and `python3 scripts/package.py --submission-ready`. Record the final SHA-256 and revisions.
7. Stop before either final Submit button. Submission and later public listing publication require the user's instruction. After approval, update onboarding with the actual directory links; do not invent them or remove the legacy MCP connection prematurely.

Sources and compatibility notes are maintained in [publication.md](./publication.md).

OpenAI's portal requests the account `email` identity scope as part of its OIDC flow. The OpenAI ZIP explicitly declares that scope alongside the five Fusionmetrics permissions, so DCR registration and authorization agree. Clerk allows it only through fresh consent; setup-only defaults are unchanged. Native Codex and Claude Code use the five Fusionmetrics scopes; the generic authorization challenge must match them. The email identity scope identifies the signed-in account; it does not grant mail access.
