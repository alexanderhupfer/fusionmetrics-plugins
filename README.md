# Fusionmetrics plugins

Publication candidate for Codex and Claude Code. No directory submission has been made.

The [Fusionmetrics plugin](./plugins/fusionmetrics/README.md) connects to https://fusionmetrics.com/api/mcp through browser OAuth. It provides the existing read-only analytics capabilities, App Store listing optimization, GA4/BigQuery onboarding, revenue import setup, and optional contact capture. Google administration and Shopify listing changes use the Partner's authorized browser. The package contains public integration files only; it contains no Fusionmetrics application source, credentials, or Partner data.

[Publication checklist](./docs/publication.md) · [Support](./plugins/fusionmetrics/SUPPORT.md) · [MIT license](./LICENSE)

The marketplace catalogs support development and testing. Availability of custom marketplaces varies by client. In Claude Code desktop, open Plugins and add this repository as a marketplace, then install Fusionmetrics. Codex supports repo marketplaces for local testing; the public no-command install button requires an approved directory listing. See the official client documentation linked in the publication guide.

Version 0.2.0 requires analytics authorization and the matching hosted GA4 tools. Keep the existing analytics connection until the replacement passes client validation. This candidate does not retire the legacy endpoint.

Maintainers: run python3 scripts/validate.py and python3 scripts/package.py. These commands validate and build a ZIP locally. They do not submit or publish a listing. CI uploads the same candidate as a build artifact.

The MIT license covers this repository's plugin materials only, not the Fusionmetrics application or hosted service.
