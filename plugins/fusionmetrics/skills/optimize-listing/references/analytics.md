# Fusion Metrics keyword analysis

Use the prepared Fusion Metrics views only. Do not query the connected GA4 or BigQuery dataset directly.

## Interpretation rules

- Define a search-attributed listing view as a distinct `entity_key` in `funnel_events` with `step_key = 'app_listing_page_view'` and a non-empty `search_term`.
- Define an add-app click as a distinct `entity_key` with `step_key = 'add_app_button_clicked'`.
- Report listing-to-add-app rate only; do not call it an install or trial conversion rate.
- Treat revenue as exact-only, sparse attribution. `transaction_count` counts billing transactions, not merchants. Use only positive gross revenue when calculating contribution share; retain signed revenue for context.
- Treat historical rank as observed rank on visits that reached the listing. It is not proof of a human visit. Missing rank is unknown, not zero and not proof that the app never ranked.
- Normalize terms with lowercase, trim, and whitespace collapse. Preserve word order and do not stem because exact phrase order can affect live search.
- Classify evidence by percentage contribution, not absolute volume. Absolute views, clicks, transactions, and currency values may appear only as audit context and to explain uncertainty.

## Use all history with continuous recency

Do not impose a universal day window or a minimum traffic requirement. Include the app's full observed history. Within each available signal, map the oldest observed date to 0%, the newest to 100%, and each intervening date to its proportional position in that span. If a source contains a single date, assign 50% to every row.

For each term, compare its mean temporal position with the app-wide mean for the same signal. Report the difference as `recency_lift_pp`:

- positive means that signal for the term skews newer than the app's overall signal;
- negative means it skews older;
- zero means no relative skew or no usable time span.

This keeps every event in the analysis and makes recency continuous. It avoids a fixed recent-window boundary that would discard too much evidence for sparse apps or over-aggregate dense apps.

## Opportunity query

Run this over the complete prepared dataset:

```sql
WITH
view_entities AS (
  SELECT
    lower(regexp_replace(trim(search_term), '\s+', ' ', 'g')) AS search_term,
    entity_key,
    min(CAST(date AS DATE)) AS event_date
  FROM funnel_events
  WHERE step_key = 'app_listing_page_view'
    AND search_term IS NOT NULL
    AND trim(search_term) <> ''
  GROUP BY 1, 2
),
view_bounds AS (
  SELECT min(event_date) AS first_date, max(event_date) AS last_date
  FROM view_entities
),
view_events AS (
  SELECT
    view_entities.*,
    CASE
      WHEN first_date = last_date THEN 50.0
      ELSE 100.0 * date_diff('day', first_date, event_date)
        / nullif(date_diff('day', first_date, last_date), 0)
    END AS temporal_position_pct
  FROM view_entities, view_bounds
),
views AS (
  SELECT
    search_term,
    count(*) AS listing_views,
    avg(temporal_position_pct) AS traffic_recency_pct
  FROM view_events
  GROUP BY 1
),
view_global AS (
  SELECT avg(temporal_position_pct) AS app_traffic_recency_pct
  FROM view_events
),
click_entities AS (
  SELECT
    lower(regexp_replace(trim(search_term), '\s+', ' ', 'g')) AS search_term,
    entity_key,
    min(CAST(date AS DATE)) AS event_date
  FROM funnel_events
  WHERE step_key = 'add_app_button_clicked'
    AND search_term IS NOT NULL
    AND trim(search_term) <> ''
  GROUP BY 1, 2
),
click_bounds AS (
  SELECT min(event_date) AS first_date, max(event_date) AS last_date
  FROM click_entities
),
click_events AS (
  SELECT
    click_entities.*,
    CASE
      WHEN first_date = last_date THEN 50.0
      ELSE 100.0 * date_diff('day', first_date, event_date)
        / nullif(date_diff('day', first_date, last_date), 0)
    END AS temporal_position_pct
  FROM click_entities, click_bounds
),
clicks AS (
  SELECT
    search_term,
    count(*) AS add_app_clicks,
    avg(temporal_position_pct) AS click_recency_pct
  FROM click_events
  GROUP BY 1
),
click_global AS (
  SELECT avg(temporal_position_pct) AS app_click_recency_pct
  FROM click_events
),
ranks AS (
  SELECT
    lower(regexp_replace(trim(search_term), '\s+', ' ', 'g')) AS search_term,
    min(organic_rank) AS best_observed_rank,
    round(avg(organic_rank), 2) AS average_observed_rank,
    arg_max(organic_rank, event_timestamp) AS latest_observed_rank,
    count(*) AS rank_observations
  FROM listing_page_views
  WHERE search_term IS NOT NULL
    AND trim(search_term) <> ''
    AND organic_rank IS NOT NULL
  GROUP BY 1
),
revenue_rows AS (
  SELECT
    lower(regexp_replace(trim(search_term), '\s+', ' ', 'g')) AS search_term,
    CAST(date AS DATE) AS event_date,
    gross_earnings,
    net_earnings,
    transaction_count
  FROM revenue_by_source
  WHERE search_term IS NOT NULL
    AND trim(search_term) <> ''
),
revenue_bounds AS (
  SELECT min(event_date) AS first_date, max(event_date) AS last_date
  FROM revenue_rows
),
revenue_temporal AS (
  SELECT
    revenue_rows.*,
    greatest(gross_earnings, 0) AS positive_gross_earnings,
    CASE
      WHEN first_date = last_date THEN 50.0
      ELSE 100.0 * date_diff('day', first_date, event_date)
        / nullif(date_diff('day', first_date, last_date), 0)
    END AS temporal_position_pct
  FROM revenue_rows, revenue_bounds
),
revenue AS (
  SELECT
    search_term,
    round(sum(gross_earnings), 2) AS gross_earnings,
    round(sum(net_earnings), 2) AS net_earnings,
    sum(transaction_count) AS transaction_count,
    sum(positive_gross_earnings) AS positive_gross_earnings,
    sum(positive_gross_earnings * temporal_position_pct)
      / nullif(sum(positive_gross_earnings), 0) AS revenue_recency_pct
  FROM revenue_temporal
  GROUP BY 1
),
revenue_global AS (
  SELECT
    sum(positive_gross_earnings * temporal_position_pct)
      / nullif(sum(positive_gross_earnings), 0) AS app_revenue_recency_pct
  FROM revenue_temporal
),
terms AS (
  SELECT search_term FROM views
  UNION SELECT search_term FROM clicks
  UNION SELECT search_term FROM ranks
  UNION SELECT search_term FROM revenue
),
metrics AS (
  SELECT
    terms.search_term,
    coalesce(views.listing_views, 0) AS listing_views,
    coalesce(clicks.add_app_clicks, 0) AS add_app_clicks,
    coalesce(revenue.gross_earnings, 0) AS gross_earnings,
    coalesce(revenue.positive_gross_earnings, 0) AS positive_gross_earnings,
    coalesce(revenue.net_earnings, 0) AS net_earnings,
    coalesce(revenue.transaction_count, 0) AS transaction_count,
    views.traffic_recency_pct - view_global.app_traffic_recency_pct AS traffic_recency_lift_pp,
    clicks.click_recency_pct - click_global.app_click_recency_pct AS click_recency_lift_pp,
    revenue.revenue_recency_pct - revenue_global.app_revenue_recency_pct AS positive_revenue_recency_lift_pp,
    ranks.latest_observed_rank,
    ranks.average_observed_rank,
    ranks.best_observed_rank,
    coalesce(ranks.rank_observations, 0) AS rank_observations
  FROM terms
  LEFT JOIN views USING (search_term)
  LEFT JOIN clicks USING (search_term)
  LEFT JOIN ranks USING (search_term)
  LEFT JOIN revenue USING (search_term)
  CROSS JOIN view_global
  CROSS JOIN click_global
  CROSS JOIN revenue_global
),
shares AS (
  SELECT
    *,
    CASE WHEN listing_views > 0
      THEN 100.0 * add_app_clicks / listing_views
      ELSE NULL
    END AS listing_to_add_app_pct,
    coalesce(100.0 * listing_views / nullif(sum(listing_views) OVER (), 0), 0) AS traffic_share_pct,
    coalesce(100.0 * add_app_clicks / nullif(sum(add_app_clicks) OVER (), 0), 0) AS add_app_click_share_pct,
    coalesce(100.0 * positive_gross_earnings / nullif(sum(positive_gross_earnings) OVER (), 0), 0) AS positive_revenue_share_pct,
    CASE
      WHEN listing_views > 0 AND sum(add_app_clicks) OVER () > 0
        THEN (1.0 * add_app_clicks / listing_views)
          / nullif(1.0 * sum(add_app_clicks) OVER () / sum(listing_views) OVER (), 0)
      ELSE NULL
    END AS conversion_efficiency_index
  FROM metrics
)
SELECT
  search_term,
  round(traffic_share_pct, 2) AS traffic_share_pct,
  round(add_app_click_share_pct, 2) AS add_app_click_share_pct,
  round(positive_revenue_share_pct, 2) AS positive_revenue_share_pct,
  round(traffic_recency_lift_pp, 2) AS traffic_recency_lift_pp,
  round(click_recency_lift_pp, 2) AS click_recency_lift_pp,
  round(positive_revenue_recency_lift_pp, 2) AS positive_revenue_recency_lift_pp,
  round(listing_to_add_app_pct, 2) AS listing_to_add_app_pct,
  round(conversion_efficiency_index, 2) AS conversion_efficiency_index,
  latest_observed_rank,
  average_observed_rank,
  best_observed_rank,
  listing_views,
  add_app_clicks,
  gross_earnings,
  net_earnings,
  transaction_count,
  rank_observations
FROM shares
ORDER BY traffic_share_pct DESC, add_app_click_share_pct DESC, positive_revenue_share_pct DESC, search_term
```

If an optional prepared view is unavailable, remove its CTE, union, joined columns, and output columns. Do not synthesize zeros for a source that does not exist; distinguish unavailable from an observed zero.

## Apply traffic-quality sensitivity

Run the query above unfiltered as the primary evidence record. If the preflight in [traffic-quality.md](traffic-quality.md) identified a suspicious cluster, rerun the affected CTEs with the same narrow country/date/surface predicate removed:

- filter `view_entities` and `click_entities` through `funnel_events` fields;
- filter `ranks` through corresponding `listing_page_views` fields;
- leave `revenue_rows` unchanged because exact attributed revenue is independent downstream evidence.

Do not remove a country wholesale and do not rewrite the primary map with filtered numbers. Compare the two maps explicitly. A changed target, guardrail set, or evidence-dominance conclusion makes selection unstable and stops a live mutation. Percentage-point differences alone are context, not a universal stability threshold.

## Build a continuous evidence profile

For every term, report the available percentage vector:

- attributable listing-traffic share;
- attributable add-app-click share;
- positive attributed gross-revenue share;
- recency lift in percentage points for each available signal;
- listing-to-add-app rate and its index relative to the app-wide rate;
- latest, average, and best observed historical rank when available.

Do not collapse this vector into fixed contribution bands or a universal weighted score. Compare terms by dominance: one term has stronger commercial evidence when it contributes an equal or larger percentage on every available acquisition signal and a larger percentage on at least one. When terms trade off signals, explain the tradeoff instead of hiding it in arbitrary weights.

Use semantic relevance and rank headroom to turn the evidence profile into an opportunity judgment:

- Protect the normalized app brand. Screen third-party and competitor brands out of target candidates.
- Favor terms with meaningful relative contribution across more than one available signal, positive or stable recency relative to the app, and useful rank headroom.
- Treat an already-strong rank as reduced upside, not an automatic exclusion.
- Treat conversion efficiency as supporting context. It is volatile when a term represents a large percentage because of very few events; describe that uncertainty but do not discard the term using a count boundary.
- For sparse evidence, let contribution shares, the full-span recency profile, semantic relevance, traffic-quality stability, and a genuinely published reversible live test carry the judgment. A term that exists only inside a suspicious cluster is unstable, not an opportunity. For dense evidence, look for consistency across traffic, clicks, revenue, recency, and rank. Do not classify the app itself by a volume cutoff.

Recommend one target. Present alternatives only when they expose a genuine signal tradeoff. Keep raw counts visible next to percentages for auditability, but never require a minimum number of views, clicks, transactions, rank observations, or revenue.

For live guardrails, protect the brand and choose terms that collectively represent the most important percentage shares across traffic, clicks, and positive revenue, plus any phrase removed from the proposed field. Use the smallest useful set and never exceed five live queries per phase because of search-rate constraints.
