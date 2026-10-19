# Publication preparation

Version 0.2.5 was submitted to OpenAI and Claude on 19 October 2026. OpenAI reports In review; the Claude Code package passed its security scan and awaits an Anthropic reviewer. Neither is approved or published, and Anthropic approved the companion MCP connector on 19 October; it is not published. Passing local validation establishes package structure, not authentication, live behavior, review approval, or availability in a directory.

## Build and validate

Run `python3 scripts/validate.py`, then `python3 scripts/package.py`. This uses only Python's standard library. CI performs the same checks and uploads the ZIP and SHA-256 checksum as build artifacts. It does not create releases, upload to either directory, or deploy Fusionmetrics.

Run `python3 -m unittest discover -s scripts -v` for archive containment and scope tests. With Claude Code installed, run `claude plugin validate plugins/fusionmetrics` and `claude plugin validate .`. The package validator is a focused project check, not a replacement for either platform's schema and portal validation.

Maintain publication metadata and readiness evidence in this repository. The Fusionmetrics application contains a bootstrap generator; compare later exports before copying changes here so completed listing metadata is not replaced with pending placeholders. Bump all manifests' versions together when changing an installable plugin. Keep internal evidence and reviewer credentials outside this public repository.

The OpenAI ZIP contains `plugins/fusionmetrics/` at its root, without marketplace, repository, or review-status files. The builder transforms only the ZIP's `mcp.json`, adding OpenAI's documented `extensions.com.openai.auth` policy. Repository manifests remain URL-only for native-client compatibility. On 18 October 2026, the published Agent Plugins 1.0.0 MCP schema and native Codex CLI 0.162.0-alpha.17.2 rejected this per-server extension, while OpenAI's submission documentation required advanced OAuth settings in the uploaded manifest. Treat the ZIP as an OpenAI portal candidate, not a native-client installation archive. OpenAI subsequently accepted this ZIP, completed OAuth/domain verification and scanned all five skills and 15 MCP tools. Native clients continue to use the repository manifests; the ZIP extension is specific to the OpenAI portal.

`openai-connection.json` is build input for the ZIP's OAuth policy: DCR, the production resource, OIDC enabled, and `openid email user:org:read setup:read setup:write analytics:read`. OpenAI's OIDC flow needs the account-email scope; the five native-client scopes omit `email`. The input file itself is excluded from the ZIP. The current portal has no advanced OAuth settings editor; changing this file requires rebuilding and re-uploading the candidate. Inspect the actual consent request after upload. If the portal cannot request the declared permissions, keep submission blocked. Claude's manifest points to `.claude-mcp.json`, which pins the five native scopes. Local Codex marketplace tests must also verify the grant; the portable manifest alone does not pin Codex scopes. The canonical server's initial OAuth challenge must offer all five plugin scopes so clients that follow it can discover analytics. Older setup-only grants require reauthorization. Declarations do not prove live interoperability.

Clerk currently issues access JWTs with a one-day lifetime. Revoking a grant prevents refresh, but does not invalidate an already-issued JWT before expiry. The service checks current Organization membership on every MCP request. A live test on 18 October 2026 confirmed refresh returned `invalid_grant` after revocation while the issued JWT remained usable, followed by a successful normal Codex reconnection. Do not describe disconnection as immediate server-side invalidation of issued access tokens. See [Clerk's revocation contract](https://clerk.com/docs/reference/backend/oauth-applications/revoke-token).

Use [the submission packet](./submission-packet.md) for listing fields, tool annotations, data-handling answers, reviewer provisioning, live tests, and the demo scene plan. `python3 scripts/probe_public.py` checks public production metadata without credentials or mutations. Its JSON report is diagnostic evidence, not a substitute for authenticated client tests. Exit status 1 means a public check failed; it never changes readiness gates automatically.

After the reviewer completes normal OAuth, `scripts/probe_authenticated.py` can check the deployed revision, all 15 tool annotations, the expected review Organization, the selected App's recorded fixture totals, setup/GA4 status and three analytics rejection cases. Supply an existing OAuth access token in an owner-readable-only file outside the repository, plus a private fixture JSON containing `organizationId`, `appKey`, `expectedRows`, `expectedSha` and `pluginCommit`. Run with `--access-token-file`, `--fixture-file` and `--output`; `--help` describes the arguments. The output file is created with mode 0600 outside the repository. The script refuses setup/GA4 mutation tools and redirected authenticated requests, and stops before analytics if the Organization differs. Its SQL rejection probe attempts only a temporary in-memory table and a nonexistent file path. This operator probe does not replace native-client sign-in, assistant-prompt cases, real imports, revocation or legacy parity tests. Neither its tests nor an unexecuted probe establish live readiness.

For a submission-readiness check, run `python3 scripts/validate.py --submission-ready`. That check must fail until every item in `readiness.json` has supporting evidence and the required metadata and review recording are present. The publisher authorized submitting the tested package with the incomplete provider-browser coverage disclosed. Connector pairing is also tracked as pending until the portal confirms it. The readiness check intentionally continues to fail while that coverage gate is pending; submission is not evidence that all coverage is complete. Credentials and recordings containing private information belong outside Git.

## Codex and ChatGPT

1. Use the intended publisher's verified OpenAI organization and a project eligible for MCP submissions. Confirm submission permissions and global data residency.
2. Complete `readiness.json`, run the exactly five positive and three negative packaged test cases with the existing reviewer Organization, and record the results privately. Broader publisher scenarios live in `docs/extended-test-cases.json` outside the ZIP. The cases are proposed tests; none is asserted to have passed by its presence there.
3. Confirm that `extensions.com.openai.interface.termsOfServiceURL` points to the approved, publicly deployed hosted service terms page. The proposed production URL is `https://fusionmetrics.com/terms`; a local page draft or a configured URL does not prove it is live. Review the terms and their acceptance flow before adoption. The MIT license covers the plugin package only and is not a substitute for hosted service terms.
4. Add a reviewer-accessible video URL to `extensions.com.openai.review.demo_recording_url`. The recording must demonstrate the actual test cases. Supply reviewer credentials through the portal, never in this repository or its ZIP.
5. When preparation is authorized, build and upload the ZIP at https://platform.openai.com/plugins for draft validation. Complete the portal-supplied domain challenge, inspect the manifest-derived OAuth connection and tool scan, and resolve findings. A draft upload is not a directory submission. Do not accept final compliance attestations or click Submit during preparation.
6. Submit for review only after explicit authorization. Publish an approved listing only when requested. Save the real directory URL for the Fusionmetrics onboarding button; do not invent a listing link.

Use the production endpoint `https://fusionmetrics.com/api/mcp` for a public listing. Staging packages and credentials remain isolated. A reviewer account needs seeded, non-personal data and sign-in that does not depend on the founder completing an OTP, MFA, or Google account challenge. Check the configured Clerk sign-in path; do not weaken authentication for existing Partners.

Reuse the existing iPhone App Review account and fictional Organization, as specified in the submission packet. The packaged sample-data cases require Fusionmetrics sign-in only; do not require reviewers to create or supply a Shopify Partner account. Keep credentials private and preserve the iPhone review baseline. Publisher-controlled Shopify tests remain separate, and coverage of the remaining exposed write tools must be resolved before submission. See the packet's reviewer/publisher access distinction. Verify current plugin OAuth and fixture coverage before marking reviewer readiness complete; prior native-app sign-in does not verify the plugin connection.

## Claude Code

Submit from the Claude organization that should own the listings long term. The publishing account must have a paid plan and the required role. Connect a GitHub account with push access to this repository.

There are two submissions in https://claude.ai/directory/manage:

- MCP connector: `https://fusionmetrics.com/api/mcp`.
- Plugin bundle: this GitHub repository, plugin path `plugins/fusionmetrics`, tracked branch `main`.

Submit the connector and bundle from the same organization and pair them. The repository must be public before the listing goes live. Before submitting, use the portal's Validate step: the local `claude plugin validate` command does not check all directory rules. Complete data-handling and compliance answers from verified service behavior, then obtain the user's authorization for the submission and its attestations.

## Capability and migration contract

The setup workflow and official-template recipe are bundled and versioned for directory review; plugin installation does not delegate behavioral updates to a remote instruction tool. Native MCP clients can continue using the existing instruction tool.

The five bundled skills route requests to setup, existing analytics, listing optimization, and GA4/BigQuery onboarding. The four analytics operations (`list_apps`, `select_app`, `describe_schema`, `run_sql`) reuse the legacy implementation, including available Merchant contacts and reviews. The plugin may therefore return personal data within the selected Organization; review privacy disclosures and use synthetic reviewer data.

GA4 uses `ga4_get_status`, `ga4_configure_dataset`, and `ga4_import_attribution`. The server validates and saves mappings through the existing application service, preserves mappings on failed validation, enforces admin/scope/billing checks, and tracks the requested import through completion or failure. This package requires the compatible hosted server to be deployed and verified before release. Until then, the skill can guide the existing browser UI without claiming MCP execution succeeded.

The browser workflow handles GA4 properties, Shopify tracking, BigQuery export links, and narrow dataset IAM grants using the Partner's own authorization. Fusionmetrics OAuth does not grant Google or Shopify administration. Test authorized permanent listing edits separately from temporary experiments: permanent edits retain the approved value; temporary experiments restore and verify the baseline even if the variant wins. Reports must distinguish saved, pending review, and publicly visible states.

Release order: deploy the compatible server through the application's CI/CD; test a fresh plugin and an upgraded setup-only grant in each intended desktop client; compare analytics results with the existing connection on the same prepared data; then merge/release the plugin candidate and request directory submission separately. Keep `/api/mcp/analytics`, bearer-token settings, and existing client installations operational during migration. Retiring the legacy connection requires a separate migration decision and explicit authorization. The plugin becomes the preferred installation and workflow package; it still uses the hosted MCP service for tools and data.

## Live release gates

- Test fresh GUI installation, browser OAuth, Organization choice, reconnect, revocation, and insufficient permission in Codex and Claude Code desktop. Record exact package revision and client versions.
- Audit every exposed tool's title and annotations against its behavior. Analytics is read-only; dataset replacement is a write, and dataset validation/import calls external services. Local metadata tests do not replace a production tool scan.
- Test each packaged review case through the published endpoint with the existing populated reviewer Organization. Verify billing entitlement and fixed synthetic data. Exercise each exposed tool separately with authorized prerequisites and resolve any reviewer access limitations; a reduced case list does not waive that coverage.
- Verify that MCP and OAuth metadata are reachable by the actual clients and review scanners. A preparation probe received Cloudflare error 1010; this was not a full client compatibility test.
- Complete OpenAI's domain-verification challenge only after the portal supplies the exact token for `/.well-known/openai-apps-challenge`. Do not invent a verification value or treat an HTTP 200 with different content as verification.
- Review privacy coverage for the data returned by tools, support links, service terms, publisher identity, and permissions before submitting.
- Verify GA4 onboarding using an isolated property/dataset, least-privilege managed access, missing-table and denied-access failures, import completion and prepared acquisition queries. Synthetic BigQuery fixtures do not require Shopify Partner access but cannot prove live tracking/export setup. Verify both listing modes under publisher-controlled, explicitly authorized Partner access with baseline recovery. Record unavailable operations as blocked; do not attach real Partner data to the reviewer Organization.
- Contact capture remains optional. It needs local repository edits and separate deployment; include supported-surface limitations in the listing and tests.

## Sources

Requirements checked on 18 October 2026:

- https://developers.openai.com/plugins/build/plugins
- https://developers.openai.com/plugins/deploy/submission
- https://developers.openai.com/plugins/deploy/app-review
- https://claude.com/docs/directory/publish
- https://claude.com/docs/plugins/pre-submission-checklist
- https://claude.com/docs/plugins/submit
- https://claude.com/docs/connectors/building/review-criteria
- https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy
- https://code.claude.com/docs/en/desktop#install-plugins

Recheck the portal requirements before submission. Neither platform guarantees a fixed review time.
