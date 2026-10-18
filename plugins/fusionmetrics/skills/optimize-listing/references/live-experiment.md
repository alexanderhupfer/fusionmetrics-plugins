# Shopify live experiment protocol

## Recommendation and live-field priority

For listing recommendations, prioritize fields this way:

1. App Store search terms: prefer this field for an exact, relevant discovery term.
2. Introduction, app details, or feature text: use only when the variant is a clearer merchant-facing description on its own merits, not merely a place to insert a keyword.

For a same-run reversible live experiment, use only a visible field whose exact publication can be verified:

1. Introduction
2. App details
3. One feature

App Store search terms are hidden from the public listing. They can be the primary analysis recommendation, but do not use them for a temporary same-run before/after rank experiment: neither a successful admin save nor an unchanged public page proves that Shopify's search index incorporated the term. Testing a search-term change requires a separate asynchronous experiment with an explicit observation window and no immediate restoration; that workflow is outside this skill's reversible live-test contract.

Use the character limit currently displayed by the Partner Admin editor as authority. Current common limits are 30 characters for app name, 62 for subtitle, 100 for introduction, 500 for app details, 80 per feature, and 20 per search term, but do not override a different limit shown in the editor.

Do not use the app-card subtitle to add keywords with the intent of improving search performance. Do not use a temporary app-name change as a rank experiment: the name is a persistent brand identifier, must stay recognizable across app surfaces, and can affect the public listing slug. App-name or subtitle improvements require a separate permanent listing decision with policy review.

Do not change multiple fields to fit a phrase. Do not keyword-stuff, add competitors, include “Shopify” as a search term, or distort the app's real capability.

## Baseline capture

Enter the published primary English listing from its Partner Admin distribution page. Record the current admin value of every optimizer-relevant field and the public listing URL before any live search or mutation. Open the public listing and record the visible original value of the field under test. Abort when the admin and public original cannot be reconciled. Exclude tracking values, analytics secrets, review contacts, support contacts, test-account data, screencasts, and reviewer instructions.

Hash or otherwise retain the exact original value of the one field under test. Immediately before saving the variant, read the field again and abort if it no longer matches the captured original.

## Live rank measurement

Navigate to `https://apps.shopify.com/search?q=<encoded-query>` once per term. Use the same browser, account, locale, and store context throughout the run.

Identify the target app by its known public listing URL or slug. Record:

- `absolute_position`: its one-based position among all visible app cards, including ads.
- `organic_position`: its one-based position among non-ad search results.
- `ads_before_app`: ad cards before the app.
- `first_page`: whether the app appears among the loaded first-page results.
- `search_id`: the URL parameter when present.

Prefer explicit result URL parameters such as `surface_type` and `surface_intra_position`. Treat `surface_type=search_ad` as an ad. If parameters are absent, count visible result cards and exclude cards visibly labeled as sponsored or ads. If the app is absent, record null positions and `first_page=false`; do not claim a rank beyond the observed page.

## Publication gate

A successful Partner Admin save proves only the saved admin value. Before the after-search phase:

1. Reload the editor and verify exact equality with the variant.
2. Inspect listing/review status for pending or rejected changes.
3. Open the known public listing URL in the same locale.
4. Verify the exact public field value equals the variant.
5. Record the publication state and verification timestamp.

Only `public_verified` permits the after-search phase. Treat `not_public`, `pending_review`, and `unknown` as inconclusive. Do not wait by repeatedly searching; search queries are measurements, not publication probes. Restore the admin original immediately when the gate fails and verify that the public listing still or again shows the original.

## Interpret the observed tradeoff

For each measured term, report its before position, after position, signed organic-rank change, and first-page transition. Evaluate those live changes alongside the term's percentage contributions to traffic, add-app clicks, and positive attributed revenue. Do not use a universal number of rank positions as a pass/fail boundary.

Use these directional labels for complete, comparable measurements:

- `favorable`: the target moves in the intended direction and the protected-term changes do not create a stronger contrary risk when interpreted in light of their percentage contribution profiles.
- `mixed`: the target improves but one or more protected terms worsen materially in the context of their percentage contributions, or the signals otherwise conflict.
- `unfavorable`: the target does not move in the intended direction, worsens, or any gain is outweighed by risk to protected percentage contribution.

If a term is absent in either phase, describe only the observed first-page transition; do not invent an off-page rank. Use `inconclusive` when rate limiting, incomplete results, or a non-comparable search context prevents the tradeoff from being evaluated.

Always restore the original field after classification. Verify exact equality in the reloaded editor and on the public listing. A favorable classification is evidence for a later permanent-change decision, not permission to retain the variant.

## Failure cleanup

After any save, put restoration in the cleanup path. On timeout, navigation failure, rate limit, user interruption, unexpected validation, or partial post-change results:

1. Return to the already-open editor.
2. Restore the exact original value.
3. Save.
4. Reload the editor and verify exact equality.
5. Open the public listing and verify the original field value.
6. Mark the experiment `inconclusive_restored` only after the required admin and public checks pass.

Do not retry blocked searches in the same run. Do not perform a restoration search by default; direct public-field equality is the restoration authority. If a previously public variant remains visible because publication or review is asynchronous, report cleanup as incomplete and continue the authorized restoration workflow rather than claiming a restored status.
