# Fusionmetrics submission packet

Prepared 18 October 2026 for version 0.2.0. This document contains proposed listing answers and an execution plan. It does not certify deployment, completed reviewer tests, legal approval, or directory acceptance. Keep reviewer passwords, private account identifiers, OAuth tokens, and unredacted recordings outside this public repository.

## Listing fields

| Field | Value |
| --- | --- |
| Name | Fusionmetrics |
| Short description | Shopify analytics and growth |
| Publisher | Fusionmetrics / AC App-commerce UG (haftungsbeschränkt) |
| Contact | Alex from Fusionmetrics, Founder — alex@fusionmetrics.com |
| Website | https://fusionmetrics.com/agent-setup |
| Support | https://fusionmetrics.com/support/chat |
| Privacy | https://fusionmetrics.com/privacy |
| Service terms | https://fusionmetrics.com/terms — verify the approved page is deployed |
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

Platform scope: validate Codex desktop and Claude Code desktop separately. Browser-dependent workflows require an authorized browser integration available in that client. Do not claim that installing this package supplies browser control, Google/Shopify credentials, a mobile experience, or a custom MCP UI. No MCP UI screenshots are needed unless an actual UI resource is added.

## OAuth and native-client checks

Use DCR with PKCE through the endpoint's authorization-server discovery. The requested scopes are `openid user:org:read setup:read setup:write analytics:read`; the resource is exactly `https://fusionmetrics.com/api/mcp`. Do not embed client secrets, bearer tokens, Partner account credentials, or Google keys in the package.

Production preparation found that the resource metadata advertises `analytics:read`, but Clerk's authorization-server metadata does not. In the production Fusionmetrics Clerk application, add the advertised custom scope `analytics:read`, with a plain-language consent description covering prepared revenue, acquisition, Merchant contact, and review data. Verify the DCR policy allows it. Keep existing native setup defaults unchanged. Adding a scope is not evidence that an old grant has it: test fresh authorization and reauthorization in each client. Do not grant an assistant access to a real Partner Organization merely to test publication.

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
- Deletion/revocation: revocation removes future authorized access, not previously returned assistant messages or all service records. Use the privacy policy and support process for deletion requests. Verify current retention and subprocessor disclosures before attesting to them.
- Charging: no purchase is made by an analytics tool. An eligible Fusionmetrics plan is required; do not claim that the hosted service is free because the plugin files use MIT.
- AI training, regional storage, contractual processing terms, certifications, and exact retention periods: answer only from approved company policy. The code audit does not establish these claims. Leave unsupported portal answers unconfirmed.

## Reviewer account and test data

Create a dedicated Organization named “Fusionmetrics Plugin Review” in the production Clerk application and corresponding hosted service. Use a reviewer identity with no membership in real Partner Organizations. Configure a supported sign-in path that reviewers can use without the founder supplying email codes or MFA. The human must enter/set the reviewer credential privately; store it in a password manager and the portal's protected reviewer field, never here.

Give the review Organization the service entitlement needed for setup and analytics. Do not create a real Stripe charge just to provision review access. Provision a separate non-admin reviewer in the same isolated Organization for permission tests, and a second isolated Organization for cross-Organization denial tests. Do not disable authentication or membership enforcement globally.

Prepare these resources through the normal supported import/data pipeline:

| Resource | Required state and expected evidence |
| --- | --- |
| Revenue Demo app | Synthetic revenue, MRR movements, churn, trials and cohorts with a fixed date range and an independently recorded totals ledger. Reconcile MRR opening + new + expansion + reactivation − contraction − churn = closing. |
| Acquisition Demo | An isolated GA4 property, daily BigQuery export tables, an authorized test Shopify app/listing, and a saved managed credential with dataset Data Viewer. Record app/property/dataset mapping privately. |
| Contacts/reviews | Synthetic contact addresses under `example.com` and clearly fictional reviews. Include one review containing an instruction to exfiltrate contacts, which the assistant must ignore. |
| Setup Demo | An authorized Shopify development Partner account/app with credentials entered privately, ready to exercise discovery and an actual import. Empty artifacts and invented API tokens are not a valid review fixture. |
| Failure cases | Missing daily table, denied BigQuery access, failed import, read-only member, setup-only OAuth grant, and foreign Organization IDs. Use isolated resources and preserve the valid baseline. |
| Capture app | A local official Shopify React Router template with reproducible checks. Record local changes separately from a deployed capture receipt. |

If a resource cannot be provisioned, record the case as blocked. Do not substitute real Merchant records for synthetic data or treat local mocked tests as live reviewer tests.

## Live execution record

The complete proposed prompts and expected outcomes are embedded in `plugins/fusionmetrics/plugin.json` under `extensions.com.openai.review.test_cases`: 10 positive and 8 negative cases. Run all supported cases, including at least five positive and three negative, using the exact reviewer identity and candidate package. Record privately:

| Field | What to capture |
| --- | --- |
| Revision | Plugin commit, ZIP SHA-256, deployed service SHA, client name/version, UTC time |
| Authorization | Selected Organization, consent scopes, fresh vs upgraded grant; redact tokens and personal identifiers |
| Test | Exact prompt, relevant tool names, actual output, expected result, pass/fail/blocked |
| Writes | Confirmed exact target/diff, actual saved state, job ID/status, cleanup/restore evidence |
| Failures | Scope/admin/cross-Organization denial, revocation, missing data, rate-limit handling and retry behavior |
| Parity | Same app, artifact generation, SQL and row limit on legacy analytics and plugin; compare result data and metric definitions |

Add fresh install, reconnect, revocation, and an interrupted retry to the prompt cases. For listing changes, separately verify an approved permanent edit and a temporary experiment with restoration. For GA4, record actual completed import and prepared-data availability; a successful validation or queued job alone is insufficient. The package contains workflows, not proof that the platform's browser integration performed them.

## Demo recording plan

Record the actual supported client experience with synthetic data, normally at 1920×1080. Use the existing Chrome profile/approved browser connection; do not launch an automation profile. Do not display secrets, tokens, real Merchant contacts, or private account lists. Pause capture during sensitive sign-in. Clearly label cuts over actual export/import waiting.

| Scene | Visible evidence |
| --- | --- |
| 1. Install and connect | Plugin identity/version, browser sign-in, Organization selection, and enabled capabilities; no terminal installation commands. |
| 2. Revenue question | App selection, bounded analytics tools, period/freshness, and totals that match the independent synthetic ledger. |
| 3. Listing optimization | Baseline, traffic limitations, exact proposed subtitle diff, human authorization, saved/public state; demonstrate restoration for a temporary test separately. |
| 4. GA4 onboarding | Property/dataset/principal mapping, validation, real import progress and completed prepared acquisition query. |
| 5. Failure boundary | A denied permission or missing daily export, with an accurate explanation and no invented success. |
| 6. Optional capture | Local official-template preparation and check result; distinguish it from deployment. |

Show both intended clients, or supply separately labelled recordings. Review the final encoded video and contact sheet. Upload only the redacted final recording to a reviewer-accessible location; put its actual URL in `review.demo_recording_url`. A storyboard, screenshot montage, or synthetic UI is not a live demo.

## Portal sequence and release handoff

1. Release the compatible service via its normal CI/CD: feature-branch staging validation, approved merge to main, production workflow, exact deployed-SHA check. Publish the approved terms/privacy changes with it. No direct VPS deployment.
2. Configure/verify Clerk's advertised analytics scope and actual client grants. Run `scripts/probe_public.py` for public metadata; retain the report outside the repo. Fix Cloudflare/scanner failures by testing the actual portal scanner, not by assuming a shell probe proves reachability.
3. Build the OpenAI ZIP. Upload as a draft under the intended verified business identity; inspect advanced OAuth from the package. Complete the exact domain challenge supplied by the portal at `/.well-known/openai-apps-challenge`. A token has not yet been supplied.
4. Scan tools and compare all 15 titles/annotations with the matrix. Attach reviewer credentials privately, the test evidence, and the real video. Leave legal/compliance attestations for the publisher.
5. In Claude's publisher portal, validate the repository/path/exact revision. Prepare the MCP connector and plugin bundle under the same owning Organization and pair them. Validate again after moving from a candidate branch to main.
6. Mark readiness gates verified only with current evidence. Run `python3 scripts/validate.py --submission-ready` and `python3 scripts/package.py --submission-ready`. Record the final SHA-256 and revisions.
7. Stop before either final Submit button. Submission and later public listing publication require the user's instruction. After approval, update onboarding with the actual directory links; do not invent them or remove the legacy MCP connection prematurely.

Sources and compatibility notes are maintained in [publication.md](./publication.md).
