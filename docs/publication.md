# Publication preparation

This repository is a publication candidate. It has not been submitted to either directory. Passing local validation establishes package structure, not authentication, live behavior, review approval, or availability in a directory.

## Build and validate

Run `python3 scripts/validate.py`, then `python3 scripts/package.py`. This uses only Python's standard library. CI performs the same checks and uploads the ZIP and SHA-256 checksum as build artifacts. It does not create releases, upload to either directory, or deploy Fusionmetrics.

Run `python3 -m unittest discover -s scripts -v` for archive containment and scope tests. With Claude Code installed, run `claude plugin validate plugins/fusionmetrics` and `claude plugin validate .`. The package validator is a focused project check, not a replacement for either platform's schema and portal validation.

Maintain publication metadata and readiness evidence in this repository. The Fusionmetrics application contains a bootstrap generator; compare later exports before copying changes here so completed listing metadata is not replaced with pending placeholders. Bump all manifests' versions together when changing an installable plugin. Keep internal evidence and reviewer credentials outside this public repository.

The OpenAI ZIP contains the validated contents of `plugins/fusionmetrics/` at its root, without marketplace, repository, or review-status files. Both the source and ZIP's portable `mcp.json` stay URL-only. On 18 October 2026, the published Agent Plugins 1.0.0 MCP schema rejected the per-server `extensions.com.openai.auth` field documented by OpenAI; native Codex CLI 0.162.0-alpha.17.2 also rejected server extensions. Do not insert that extension into this archive until the relevant schema and clients support it.

`openai-connection.json` records the production endpoint, DCR authentication, resource, and setup-only base/default scopes for manual connection configuration in the OpenAI portal. It is maintainer input, not an installable manifest, and is excluded from the ZIP. Apply those settings in the portal and inspect the actual consent request. If the portal cannot preserve setup-only permissions, keep submission blocked and resolve the client configuration rather than accepting broader access. Claude's manifest points to `.claude-mcp.json`, which pins the same setup scopes. Local Codex marketplace tests must also verify the grant; this portable manifest alone does not pin Codex scopes. Declarations do not prove live interoperability.

For a submission-readiness check, run `python3 scripts/validate.py --submission-ready`. That check must fail until every item in `readiness.json` has supporting evidence and the required metadata and review recording are present. Credentials and recordings containing private information belong outside Git.

## Codex and ChatGPT

1. Use the intended publisher's verified OpenAI organization and a project eligible for MCP submissions. Confirm submission permissions and global data residency.
2. Complete `readiness.json`, run the packaged positive and negative test cases with a dedicated reviewer Organization, and record the results privately. The cases in `plugin.json` are proposed tests; none is asserted to have passed by its presence there.
3. Confirm that `extensions.com.openai.interface.termsOfServiceURL` points to the approved, publicly deployed hosted service terms page. The proposed production URL is `https://fusionmetrics.com/terms`; a local page draft or a configured URL does not prove it is live. Review the terms and their acceptance flow before adoption. The MIT license covers the plugin package only and is not a substitute for hosted service terms.
4. Add a reviewer-accessible video URL to `extensions.com.openai.review.demo_recording_url`. The recording must demonstrate the actual test cases. Supply reviewer credentials through the portal, never in this repository or its ZIP.
5. Build the ZIP, then, only when submission is requested, upload it at https://platform.openai.com/plugins. Complete domain verification, configure the production MCP connection from `openai-connection.json`, inspect OAuth scopes and tool scans, and resolve findings.
6. Submit for review only after explicit authorization. Publish an approved listing only when requested. Save the real directory URL for the Fusionmetrics onboarding button; do not invent a listing link.

Use the production endpoint `https://fusionmetrics.com/api/mcp` for a public listing. Staging packages and credentials remain isolated. A reviewer account needs seeded, non-personal data and sign-in that does not depend on the founder completing an OTP, MFA, or Google account challenge. Check the configured Clerk sign-in path; do not weaken authentication for existing Partners.

## Claude Code

Submit from the Claude organization that should own the listings long term. The publishing account must have a paid plan and the required role. Connect a GitHub account with push access to this repository.

There are two submissions in https://claude.ai/directory/manage:

- MCP connector: `https://fusionmetrics.com/api/mcp`.
- Plugin bundle: this GitHub repository, plugin path `plugins/fusionmetrics`, tracked branch `main`.

Submit the connector and bundle from the same organization and pair them. The repository must be public before the listing goes live. Before submitting, use the portal's Validate step: the local `claude plugin validate` command does not check all directory rules. Complete data-handling and compliance answers from verified service behavior, then obtain the user's authorization for the submission and its attestations.

## Live release gates

- Test fresh GUI installation, browser OAuth, Organization choice, reconnect, revocation, and insufficient permission in Codex and Claude Code desktop. Record exact package revision and client versions.
- Audit every exposed tool's title and annotations against its behavior. The setup server's current common metadata needs review; do not treat write tools as read-only or blanket every tool as open-world.
- Test each proposed review case through the published endpoint with a dedicated, populated reviewer Organization. Verify billing entitlement and sample imports without real Merchant data.
- Verify that MCP and OAuth metadata are reachable by the actual clients and review scanners. A preparation probe received Cloudflare error 1010; this was not a full client compatibility test.
- Complete OpenAI's domain-verification challenge only after the portal supplies the exact token. No token or route has been invented here.
- Review privacy coverage for the data returned by tools, support links, service terms, publisher identity, and permissions before submitting.
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
- https://code.claude.com/docs/en/desktop#install-plugins

Recheck the portal requirements before submission. Neither platform guarantees a fixed review time.
