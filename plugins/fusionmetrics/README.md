# Fusionmetrics

Version 0.2.3. Endpoint: https://fusionmetrics.com/api/mcp.

Analyze Shopify app revenue, MRR, churn, trials, Merchant activity and available contacts, reviews, and acquisition attribution using the existing read-only Fusionmetrics MCP tools. Optimize Shopify App Store listings with prepared traffic and revenue evidence and authorized browser edits. Set up revenue imports and GA4/BigQuery acquisition data: inspect connection status, validate and save a dataset mapping, and start imports. Google property/export/IAM configuration and Shopify listing changes use your signed-in browser and require authorization. Credentials stay in browser forms. Optional Merchant contact capture supports Shopify's official React Router template and requires local repository access and separate deployment. The plugin requests analytics read and setup read/write permissions; setup writes require an Organization administrator. A Fusionmetrics account and eligible service plan are required. Existing MCP connections remain available during migration.

Ask “Explain my app's revenue changes”, “Optimize my Shopify App Store listing”, or “Set up GA4 and BigQuery for my app”. The get-started skill routes to analytics, optimize-listing, ga4-bigquery, or setup. Sign in through the assistant's browser authorization flow and select the intended Organization. Older setup-only grants need analytics authorization. Enter Partner API tokens, Shopify Client Secrets, and any Google service-account keys only in the designated browser forms, never in chat or committed files.

This package contains five skills, reference documents, an optional local Python validator for listing experiments, manifests, and artwork. It has no hooks, bundled executable MCP server, or API keys. Fusionmetrics serves data and enforces permissions. The assistant uses an authorized browser for Google configuration and Shopify listing edits; the plugin does not grant those accounts access. Listing recommendations can run without edits; live experiments restore the baseline, while an authorized permanent update retains the approved changes.

This is a publication candidate. The new GA4 tools require the matching hosted server deployment. Local packaging checks do not prove a live connection. Existing analytics MCP connections remain supported during migration. See the repository's publication checklist for client validation and review status. After directory publication, installation and browser sign-in can be completed from the assistant's plugin UI.

[Support](./SUPPORT.md) · [Privacy](https://fusionmetrics.com/privacy)

MIT applies to the files in this plugin package. It does not license the Fusionmetrics application or replace hosted service terms.

OpenAI directory connections also request your account email for sign-in. Native Codex and Claude Code use the five Fusionmetrics identity, Organization, setup and analytics scopes. All clients require consent for the selected Organization.
