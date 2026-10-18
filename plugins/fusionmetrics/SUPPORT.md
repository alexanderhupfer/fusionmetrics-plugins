# Fusionmetrics plugin support

Contact **Alex from Fusionmetrics, Founder**, at [alex@fusionmetrics.com](mailto:alex@fusionmetrics.com).

Include the assistant and version, plugin version, workflow, and the error message. Remove credentials, Merchant details, and other private information from any screenshots or logs. Never send a Shopify Partner API token, Shopify Client Secret, Google service-account key, OAuth token, or MCP bearer token.

For connection problems, reconnect using the assistant's sign-in flow and select the intended Fusionmetrics Organization. Analytics requires `analytics:read`; old setup-only grants must be reauthorized. An Organization admin with `setup:write` must authorize setup and GA4 mapping/import changes. If the assistant reports an interrupted import, ask it to read the current setup or GA4 status before retrying.

Analytics uses Fusionmetrics' prepared data. A missing dataset or GA4 export cannot be replaced by invented results. GA4 daily exports may take time to appear. Google configuration and Shopify listing edits need a supported browser connected to the Partner's authorized account; Fusionmetrics OAuth does not authorize those accounts. If the host cannot operate that browser, guide the human through the same UI steps. No terminal commands are required from the Partner for these workflows.

Optional contact capture supports Shopify's official React Router app template; analytics and listing optimization do not require that template. Other capture frameworks require separate evaluation. Local checks confirm code preparation; a deployed app must receive a real contact before contact capture can be reported as working.

Version 0.2.0 needs the matching hosted GA4 tools. Keep the existing analytics connection until the full plugin is verified in the intended client. The legacy endpoint remains available during migration.

[Setup guide](https://fusionmetrics.com/agent-setup) · [Privacy policy](https://fusionmetrics.com/privacy)
