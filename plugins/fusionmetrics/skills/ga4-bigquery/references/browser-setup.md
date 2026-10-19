# Browser setup and recovery

Read the current official documentation before changing provider settings; UI labels, permissions, costs, and limits can change. These are setup instructions, not authority to alter an unrelated account.

## Property and tracking

In Google Analytics, choose or create the confirmed property and a web data stream for the app listing. Check the intended reporting timezone and currency. The Measurement ID starts with G-. Match that ID to the intended Shopify app listing's tracking settings. The human creates and enters the stream's Measurement Protocol API secret directly in the provider UI for server-side install events. Preserve unrelated listing fields. Verify the saved Measurement ID and configuration state without exposing the secret.

Confirm actual listing activity in the provider UI when available; do not manufacture Merchant installs. Full-funnel install events and listing views are distinct signals. A short verification visit is not proof of complete attribution history.

## Export

In GA4 Admin → Product links → BigQuery links, inspect the existing link first. Link the confirmed project, choose the authorized data location, and enable daily export. Verify the selected streams and event exclusions. Creating a project, enabling billing, or changing export location requires authorization for those specific choices; never reuse the operator's own billing/project by default.

The dataset is normally analytics_<property_id>; confirm its actual identity rather than guessing it. Fusionmetrics imports daily events_YYYYMMDD tables and excludes events_intraday_*. A newly created link may need time to produce daily tables and does not guarantee backfill. Report that waiting state explicitly.

## Access

- **Managed hosted connection:** copy the principal returned by ga4_get_status or shown in Fusionmetrics Google Cloud access. Grant BigQuery Data Viewer on the export dataset only. The managed runtime provides its own Storage Read project permissions. Do not grant project-wide access merely to make dataset discovery work; managed discovery is intentionally unavailable.
- **Partner-provided credential:** the human uploads service-account JSON through the Fusionmetrics browser form. Grant its principal BigQuery Data Viewer on the export dataset and BigQuery Read Session User on the service-account project. BigQuery Job User is optional for the SQL fallback and may incur query charges; enable it only when needed and authorized. Never request the JSON key in chat or a local repository.

Preserve existing IAM bindings and use the narrow role/scope. Verify the exact principal and dataset after saving. Report denied permissions or organization-policy restrictions; do not bypass them by broadening the grant.

## Diagnose in order

1. Check the correct listing's saved Measurement ID and stream.
2. Inspect GA4 Realtime/DebugView for listing activity; installation events require the Measurement Protocol secret.
3. Check the export link, selected streams, location, and daily export state.
4. Verify the dataset and at least one completed daily table exist. Do not issue ad hoc BigQuery SQL merely to bypass a failed Fusionmetrics connection.
5. Check the selected credential identity and dataset-level grant, then validate in Fusionmetrics.
6. Inspect the returned read mode, table suffix, event-shape warnings, and detected app slugs. Start an authorized import and verify its persisted status before reporting completion.

## Current sources

- [Shopify listing tracking](https://shopify.dev/docs/apps/launch/marketing/track-listing-traffic)
- [Google BigQuery export setup](https://support.google.com/analytics/answer/9823238?hl=en)
- [BigQuery IAM roles](https://docs.cloud.google.com/bigquery/docs/access-control)
- [Fusionmetrics setup guide](https://fusionmetrics.com/docs/ga4/bigquery-setup)

Implementation checked 18 October 2026. Provider documentation is the authority for current UI and account requirements.
