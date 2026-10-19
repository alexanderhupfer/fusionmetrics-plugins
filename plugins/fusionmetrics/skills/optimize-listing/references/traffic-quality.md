# Traffic-quality preflight

Use this preflight before treating search-attributed listing traffic or historical rank as merchant demand. The purpose is to test whether the keyword decision survives plausible acquisition contamination, not to identify bots with certainty.

## Evidence boundary

- Use prepared Fusion Metrics views only. Do not query GA4 or BigQuery directly.
- Country is a diagnostic dimension, not a bot label. Never remove an entire country merely because community reports or a traffic spike mention it.
- Prefer a concrete cluster such as country plus date span plus surface. Do not create a filter around an inconvenient keyword or result.
- Known-bot filtering upstream and zero-engagement filtering can reduce contamination, but neither proves the remaining events are human.
- Exact attributed revenue is independent downstream evidence. Keep it in both primary and sensitivity scenarios.
- If country, date, surface, or downstream-action dimensions are unavailable, say which assessment could not be performed.

## Inspect raw and eligible traffic

First distinguish all listing traffic from the search-attributed slice used by the opportunity map:

```sql
SELECT
  coalesce(country, 'Unknown') AS country,
  coalesce(surface_type, '<none>') AS surface_type,
  CASE
    WHEN search_term IS NULL OR trim(search_term) = '' THEN 'no_search_term'
    ELSE 'has_search_term'
  END AS search_term_state,
  min(CAST(date AS DATE)) AS first_date,
  max(CAST(date AS DATE)) AS last_date,
  count(*) AS page_views,
  count(DISTINCT concat(coalesce(user_pseudo_id, ''), ':', coalesce(ga_session_id, ''))) AS sessions
FROM listing_page_views
GROUP BY 1, 2, 3
ORDER BY page_views DESC, country, surface_type
```

Large direct, category, or otherwise non-search traffic can damage an overall listing conversion rate without entering the optimizer. Do not carry that traffic into a keyword sensitivity scenario unless it also appears in the search-attributed slice.

Then inspect the search-attributed funnel by country and time:

```sql
WITH events AS (
  SELECT
    date_trunc('month', CAST(date AS DATE)) AS month,
    coalesce(country, 'Unknown') AS country,
    step_key,
    lower(regexp_replace(trim(search_term), '\s+', ' ', 'g')) AS search_term,
    entity_key
  FROM funnel_events
  WHERE step_key IN ('app_listing_page_view', 'add_app_button_clicked')
    AND search_term IS NOT NULL
    AND trim(search_term) <> ''
)
SELECT
  month,
  country,
  step_key,
  count(DISTINCT entity_key) AS distinct_entities,
  count(DISTINCT search_term) AS distinct_terms
FROM events
GROUP BY 1, 2, 3
ORDER BY month, distinct_entities DESC, country, step_key
```

Drill into country, date, surface, and term only when the overview shows a concentration worth explaining. Compare views with add-app clicks, completed installs when available, and exact attributed revenue. Retain raw counts here because anomaly assessment depends on concentration and follow-through, not only contribution percentages.

## Identify a suspicious cluster

Treat a cluster as suspicious only when multiple observations agree, for example:

- an abrupt country/date concentration relative to the app's own history;
- listing views with little or no downstream progression;
- a concentration in null, direct, or unexpected surfaces;
- search-attributed terms appearing only inside the same country/date/surface cluster;
- repeated or internally inconsistent rank/search metadata.

A country concentration alone is insufficient. A low conversion rate alone is also insufficient because legitimate markets can convert differently. Record the cluster as `suspected`, not `confirmed`, unless an authoritative prepared signal explicitly classifies it.

Do not impose a universal view count, country-share percentage, conversion-rate cutoff, or anomaly score. Use the app's own history and the agreement of independent signals.

## Run the sensitivity scenario

Keep the normal, unfiltered opportunity map as the primary record. Define one narrow predicate for each evidenced suspicious cluster, using the available country, date, and surface fields. Apply the predicate consistently to:

- listing-view and add-app-click rows from `funnel_events`;
- historical-rank rows from `listing_page_views`.

Do not apply a country-only predicate. Do not remove exact attributed revenue from `revenue_by_source`; it is evidence that the acquisition path reached a real billed merchant. If a candidate has downstream evidence that conflicts with the suspected-bot interpretation, describe the conflict rather than forcing exclusion.

Recompute contribution shares, recency lift, conversion efficiency, and historical rank after removing only the suspicious cluster. Compare:

- the selected target;
- the protected/guardrail set;
- pairwise evidence dominance between serious candidates;
- whether any candidate loses all non-suspicious traffic;
- the largest traffic-share and recency-lift changes, reported as context rather than pass/fail thresholds.

Classify selection:

- `stable`: target, guardrails, and evidence-dominance conclusions survive the sensitivity scenario;
- `unstable`: any of those decision outputs changes, or the target exists only in the suspicious cluster;
- `unavailable`: the prepared views cannot support a meaningful assessment.

An unstable result stops a live listing experiment. An unavailable result permits analysis with a limitation, but do not mutate the listing when the proposed target depends primarily on unassessed traffic or rank evidence. Downstream click and exact revenue evidence can support a cautious recommendation when their provenance remains usable.

## Report the assessment

Record the assessment span, available dimensions, suspicious-cluster predicate and rationale, whether sensitivity was performed, target/guardrail/dominance stability, maximum observed share and recency changes, and limitations. Explicitly state that no blanket country exclusion was applied.
