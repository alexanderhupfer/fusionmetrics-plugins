---
name: optimize-listing
description: Optimize Shopify App Store listings using Fusionmetrics traffic, conversion, revenue, and rank evidence. Recommend listing copy, apply an explicitly authorized permanent edit, or run a reversible live experiment.
metadata:
  version: "1.1.0"
---

# Optimize Shopify App Store Keywords

Use Fusion Metrics for historical evidence and live Shopify App Store search for experiment measurement. Test historical conclusions against suspicious-traffic sensitivity before acting. For a temporary experiment, prove that the variant reached the public listing before measuring it and restore both admin and public state before finishing. For an explicitly requested permanent update, use the permanent-update workflow below.

## Resolve host capabilities

- Keep the workflow host-neutral. Do not require a Codex- or Claude-specific tool name, filesystem root, or skill-installation directory.
- Resolve Fusion Metrics MCP operations by purpose: list apps, select an app, describe its schema, and run read-only SQL. Tool namespaces may differ between hosts.
- Use the host's browser automation capability with an existing authenticated Shopify Partner session. Before browser work, load any browser-control instructions exposed by the host. Follow the host's browser policy and use its approved browser in the Partner's existing signed-in session. Do not launch a separate unauthenticated browser when the task depends on the user's signed-in state.
- Resolve bundled references and scripts relative to this `SKILL.md`. Use Python 3 for the bundled validator.
- If a required MCP operation, authenticated browser, writable artifact destination, or Python 3 is unavailable, report that capability as the blocker rather than assuming a platform-specific substitute.

## Enforce source and experiment safety

- Use only the Fusion Metrics MCP for historical traffic, click, rank, conversion, and revenue data. Never query GA4 or BigQuery directly.
- Use the Shopify Partner Admin listing editor as the authoritative listing source. Do not construct the baseline from the public listing page.
- Use the authenticated host browser selected under **Resolve host capabilities** for Partner Admin and live App Store search.
- Change exactly one listing field per experiment.
- Run one live search per selected term before and after the change. Do not poll or collect replicates.
- Do not treat a saved Partner Admin value as published. Measure the variant only after the exact public listing field is verified.
- Temporary experiments always restore the original value, even when the variant wins, and verify the public listing after restoration. An explicitly authorized permanent edit follows the separate workflow below.
- Never capture analytics secrets, contact details, test credentials, reviewer instructions, cookies, or browser storage.
- Resolve all local files at runtime. Do not assume a home directory, username, repository layout, current working directory, or installation path.

## Choose the operation

For analysis-only requests, complete historical analysis and propose an experiment without opening Partner Admin or changing anything.

For copy-only requests, use only features and placement details established by the supplied draft, the Partner, or a verified listing. Do not add a plausible feature or display location to the proposed text and rely on a disclaimer to qualify it. Keep the proposal within the known facts; list unverified details separately. Count characters exactly when reporting a count, and identify an unchecked editor limit as unverified. Synthetic acquisition fixtures are useful for demonstrating analysis, but cannot establish real keyword demand, ranking or conversion impact.

For an explicitly requested live experiment, complete the full workflow below. Show the exact field, original text, and variant before saving. If the user's request did not authorize that exact live mutation, obtain confirmation before saving it. Do not mutate the listing when traffic-quality sensitivity makes the target or guardrails unstable.

For an explicitly requested permanent update, first complete the same historical analysis and sensitivity checks. Capture the admin-authoritative baseline using step 7. Show the selected field, exact original and proposed value, rationale, and any lost phrases. Use existing authorization when it already covers that exact live change; otherwise obtain approval before saving. Re-read the original before writing, change only the authorized fields, then reload and verify the admin value and public publication state. Report pending review as pending; do not claim a published change until visible. Keep the approved value in place and retain the baseline and change report for rollback. Do not apply the temporary-experiment restoration rule to an approved permanent update. A permanent copy change is not evidence of a rank improvement.

If acquisition data is missing, use the bundled `ga4-bigquery` skill to onboard it when requested. A copy-only review may still assess clarity and factual accuracy, but label keyword demand and commercial impact as unmeasured. Historical analysis continues to use Fusionmetrics prepared data exclusively.

## Run the temporary-experiment workflow

1. **Resolve the app and Partner Admin URL.** Call `list_apps`, select the requested app, and call `describe_schema`. Record the Fusion Metrics app key, app GID, name, `partnerId` when returned, and dataset generation time. Parse the numeric Shopify app ID from the final app-GID segment. When both identifiers contain only decimal digits, construct the distribution entry URL exactly as `https://partners.shopify.com/<partnerId>/apps/<numeric-app-id>/distribution/app-store`. Do not infer `partnerId` from the app ID. Prefer the metadata-derived URL; if a supplied URL disagrees on either identifier, stop before browser work and report the mismatch. While `partnerId` is unavailable, use an exact URL supplied in task context as a compatibility fallback; otherwise ask for it.

2. **Check data readiness.** Use every available Fusion Metrics signal, but degrade gracefully. Search-attributed listing views are enough for a traffic-only opportunity map. Add clicks, revenue, and historical rank when their prepared views contain usable data. Missing optional signals narrow the conclusion; they do not disqualify an app or trigger a GA4 fallback. If there are no search-attributed listing views, report that historical keyword selection is unavailable from Fusion Metrics and stop before proposing an evidence-based target.

3. **Assess traffic quality.** Read [traffic-quality.md](references/traffic-quality.md) and inspect country, date, surface, search attribution, and downstream-action concentration using prepared Fusion Metrics views. Never label a country as bot traffic or exclude a country wholesale. When a suspicious cluster exists, define the narrow country/date/surface sensitivity predicate justified by the evidence. If the prepared views cannot support this assessment, record traffic quality as unavailable rather than assuming the traffic is clean.

4. **Build the opportunity map.** Read [analytics.md](references/analytics.md) and run its narrow query over all observed history. Do not impose a universal day window or switch horizons at a traffic cutoff. Express every term's contribution as a percentage of the app's attributable total for each signal. Express recency as continuous percentage-point lift, so every event remains usable. Use absolute counts only to explain uncertainty. Use the unfiltered map as the primary record. When step 3 found a suspicious cluster, rerun traffic, click, and historical-rank evidence with only that cluster removed; retain exact attributed revenue unchanged.

5. **Select one target.** Use the continuous percentage evidence profile in [analytics.md] together with the traffic-quality assessment. Protect branded searches and screen out third-party brand terms. Treat a strong current or historical rank as less headroom, not an automatic exclusion. Prefer a semantically relevant term whose percentage contributions show commercial value and whose rank leaves useful headroom. A traffic-only term concentrated in a suspicious cluster is uncertain unless independent downstream evidence supports it. If the target, guardrails, or evidence-dominance relationship changes under sensitivity, classify selection as unstable and stop before designing or saving a live variant. Otherwise recommend one target and, when useful, a short alternative set. Never use a minimum number of views, clicks, transactions, or revenue as an eligibility rule.

6. **Design one variant.** Read [live-experiment.md](references/live-experiment.md). Choose an eligible visible field, preserve the branded app name and merchant-facing clarity, stay inside the editor's current character limit, and avoid removing protected phrases. State a falsifiable target-rank hypothesis. App Store search terms may be the primary analysis recommendation, but they are hidden and cannot pass the public-publication gate required by this skill's same-run live test. Do not use the app-card subtitle to add keywords for search performance and do not use a temporary app-name change as a rank experiment.

7. **Capture the baseline before searching or editing.** Open the constructed distribution entry URL, choose English, and open Edit. Record the resulting locale editor URL, public listing URL, and optimizer-relevant fields in a JSON file conforming to [listing-baseline.schema.json](references/listing-baseline.schema.json). Resolve a run artifact directory at runtime: use the caller's requested destination, then a host-provided task-output location, then a unique directory in an authorized writable workspace. Save `baseline.json` there. Do not reuse or encode a machine-specific path. Record the resolved artifact location and sensitive exclusions explicitly.

8. **Choose live guardrails.** Measure the target and a small deduplicated set of protected terms. Always consider the branded query, then terms with the largest stable percentage contributions to traffic, add-app clicks, or attributed revenue, plus any important phrase removed by the variant. Size this set to the evidence available while respecting App Store search limits; never add terms merely to reach a quota. Cap the total at five terms per phase as an operational rate-limit safeguard, not an evidence threshold.

9. **Measure the live baseline.** Search each term once in the same signed-in browser context. Record absolute position, organic position excluding ads, ads before the app, first-page presence, timestamp, and search ID when exposed. A strong target rank reduces available upside but does not create a universal no-test boundary; decide whether the remaining headroom is worth the protected-term risk and explain that judgment.

10. **Publish-gate and measure the variant.** Reconfirm the editor value still matches the captured original, fill the single field, save, reload, and verify the admin value. Then open the public listing and verify that the exact field equals the variant. A pending review, unchanged public field, ambiguous rendering, or unknown publication state means the variant is not measurable: restore immediately and classify the run as inconclusive without an after-search phase. Only after exact public verification, search the same terms once each. Do not add extra searches.

11. **Restore in cleanup.** Whether measurement succeeds, fails, is interrupted, is rate-limited, or never passes the publication gate, restore the original field, save, reload, and verify exact admin equality. Open the public listing and verify the original public value too. If the variant reached the public listing, do not claim a restored result until the public original is confirmed. Do not run a third search phase unless the user explicitly requests it.

12. **Write and validate the report.** Save `experiment.json` beside `baseline.json` and follow [experiment.schema.json](references/experiment.schema.json). Record skill and schema version `1.1.0`, the traffic-quality assessment, publication state, and public restoration verification. Resolve the bundled validator relative to this `SKILL.md`, not relative to the process working directory. Run the equivalent of:

```bash
python3 <resolved-skill-directory>/scripts/validate_artifacts.py \
  --baseline <resolved-run-directory>/baseline.json \
  --experiment <resolved-run-directory>/experiment.json
```

Classify the observed tradeoff using [live-experiment.md](references/live-experiment.md). Do not turn a fixed rank delta into a universal pass/fail threshold. Use `favorable_restored`, `mixed_restored`, or `unfavorable_restored` only for complete, publicly verified measurements. Use `inconclusive_restored` for rate limits, missing results, interrupted measurement, or a variant that never passed the publication gate. Never use a restored status until both required admin and public checks pass.

## Handle search limits safely

- Search sequentially and deduplicate exact normalized terms.
- Treat a 429 response, rate-limit message, interstitial, or incomplete result set as inconclusive.
- Do not retry the blocked query in the same run.
- If the listing was already changed, restore it immediately before further analysis and verify both admin and public state.
- Ask the user before solving any CAPTCHA; prefer restoration and an inconclusive result.

## Communicate the result

State the historical span, traffic-quality assessment and sensitivity outcome, percentage contribution and recency profile, target and guardrails, exact field change, publication verification, live before/after organic positions, decision, uncertainty, and admin/public restoration verification. Call the measurement directional rather than statistically conclusive. Applying a favorable variant permanently requires a separate explicit request, handled by the permanent-update workflow above.
