---
name: get-started
description: Connect the Fusionmetrics plugin, choose an Organization, troubleshoot missing permissions, or choose between analytics, listing optimization, app setup, and GA4 onboarding.
---

# Start using Fusionmetrics

Use the bundled fusionmetrics connection at https://fusionmetrics.com/api/mcp. Sign in in the browser and select the intended Organization. The plugin requests read-only analytics plus setup read/write permissions; setup writes additionally require an Organization administrator. These permissions do not grant Google Cloud administration or Shopify listing-edit access.

Continue with the user's actual task:

- Revenue, MRR, churn, trials, Merchant activity/contacts, reviews, attribution, SQL, or reports: read [analytics](../analytics/SKILL.md). Start with list_apps; existing Partners do not need to repeat setup.
- Shopify App Store copy, search terms, or ranking opportunities: read [optimize-listing](../optimize-listing/SKILL.md).
- Connect a Shopify Partner account, configure imports, or prepare contact capture: read [setup](../setup/SKILL.md).
- Create or connect GA4, link its BigQuery export, map a dataset, or diagnose missing acquisition data: read [ga4-bigquery](../ga4-bigquery/SKILL.md).

If the requested tool is absent, inspect the available tools and the granted permissions. An older setup-only installation needs reauthorization for analytics:read; never switch Organizations or use unrelated credentials to work around a denial. Reinitialize after reconnecting because sessions are bound to identity and permissions.

This plugin uses the existing MCP analytics implementation. During migration, use one connection consistently for a task. Keep the legacy connection available until the Partner has verified equivalent access and results through the plugin; removing an old connection requires their authorization. Installing a plugin does not retire the hosted MCP endpoint.
