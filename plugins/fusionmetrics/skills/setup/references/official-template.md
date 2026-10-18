# Official Shopify React Router capture recipe

Bundled instruction version: 2026-10-18.1.

Shopify official React Router app template only:
- Inspect app/root.tsx, app/routes/app.tsx, and shopify.app.toml. Confirm the embedded app route uses AppProvider from @shopify/shopify-app-react-router/react and App Bridge v4.
- Insert one asynchronous script using the server-provided src and data-fusionmetrics-token into the authenticated app layout, alongside its existing content. Keep Shopify's AppProvider and authentication loader intact. Never put a Client Secret in client code.
- Preserve React Router rendering and hydration. Match existing JSX style, use async={true}, and avoid adding a second script on nested routes or navigation. If capture already exists, compare its public token with the selected installation and ask before replacing a different installation.
- Respect any existing Content Security Policy: use the Fusionmetrics origin for script-src and connect-src through the application's existing policy configuration. Preserve all other directives. Do not weaken the policy with wildcards.
- Run available typecheck and build scripts. Verify one script is rendered in the authenticated layout and that its origin/token match the selected installation. Plain localhost rendering cannot obtain a Shopify Admin ID token.
- After the Partner deploys, ask them to open the embedded app in Shopify Admin. Check server status for receipt; never manufacture contacts or mark a deployment complete based on local tests.
