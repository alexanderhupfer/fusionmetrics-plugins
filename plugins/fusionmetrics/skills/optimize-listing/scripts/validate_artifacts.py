#!/usr/bin/env python3
"""Validate keyword-optimizer v1.1 artifacts using only the Python standard library."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SKILL_VERSION = "1.1.0"
SKILL_DIRECTORY = Path(__file__).resolve().parent.parent
REFERENCE_DIRECTORY = SKILL_DIRECTORY / "references"
BASELINE_SCHEMA_PATH = REFERENCE_DIRECTORY / "listing-baseline.schema.json"
EXPERIMENT_SCHEMA_PATH = REFERENCE_DIRECTORY / "experiment.schema.json"

FORBIDDEN_KEY_PARTS = (
    "api_secret",
    "access_token",
    "authorization",
    "browser_storage",
    "contact_email",
    "conversion_id",
    "cookie",
    "credential",
    "instruction_notes",
    "measurement_id",
    "password",
    "pixel_id",
    "reviewer",
    "screencast",
    "support_email",
    "test_account",
)

REQUIRED_EXCLUSION_CONCEPTS = (
    ("tracking", "analytics"),
    ("credential", "password", "test account"),
    ("contact", "reviewer"),
    ("cookie", "browser storage"),
)


def normalized_query(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def value_at(root: Any, dotted_path: str) -> Any:
    value = root
    for part in dotted_path.split("."):
        if isinstance(value, list):
            value = value[int(part)]
        elif isinstance(value, dict):
            value = value[part]
        else:
            raise KeyError(dotted_path)
    return value


def walk_keys(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else key
            found.append(path)
            found.extend(walk_keys(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(walk_keys(child, f"{prefix}.{index}"))
    return found


def json_equal(left: Any, right: Any) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    return left == right


def json_type_matches(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    return False


def resolve_local_ref(root_schema: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ValueError(f"unsupported schema reference: {reference}")
    value: Any = root_schema
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        value = value[part]
    if not isinstance(value, dict):
        raise ValueError(f"schema reference is not an object: {reference}")
    return value


def valid_format(value: str, format_name: str) -> bool:
    try:
        if format_name == "date":
            date.fromisoformat(value)
            return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
        if format_name == "date-time":
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.tzinfo is not None and "T" in value
        if format_name == "uri":
            parsed = urlparse(value)
            return bool(parsed.scheme and (parsed.netloc or parsed.path))
    except (TypeError, ValueError):
        return False
    return True


def validate_schema_value(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any],
    path: str,
    errors: list[str],
) -> None:
    if "$ref" in schema:
        validate_schema_value(value, resolve_local_ref(root_schema, str(schema["$ref"])), root_schema, path, errors)
        return

    if "const" in schema and not json_equal(value, schema["const"]):
        errors.append(f"{path} must equal {schema['const']!r}")

    if "enum" in schema and not any(json_equal(value, item) for item in schema["enum"]):
        errors.append(f"{path} must be one of {schema['enum']!r}")

    expected_types = schema.get("type")
    if isinstance(expected_types, str):
        expected_types = [expected_types]
    if isinstance(expected_types, list) and not any(json_type_matches(value, item) for item in expected_types):
        errors.append(f"{path} must have type {' or '.join(expected_types)}")
        return

    if isinstance(value, str):
        if "minLength" in schema and len(value) < int(schema["minLength"]):
            errors.append(f"{path} must contain at least {schema['minLength']} characters")
        if "maxLength" in schema and len(value) > int(schema["maxLength"]):
            errors.append(f"{path} must contain at most {schema['maxLength']} characters")
        if "pattern" in schema and re.search(str(schema["pattern"]), value) is None:
            errors.append(f"{path} must match {schema['pattern']!r}")
        if "format" in schema and not valid_format(value, str(schema["format"])):
            errors.append(f"{path} must be a valid {schema['format']}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path} must be at least {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path} must be at most {schema['maximum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < int(schema["minItems"]):
            errors.append(f"{path} must contain at least {schema['minItems']} items")
        if "maxItems" in schema and len(value) > int(schema["maxItems"]):
            errors.append(f"{path} must contain at most {schema['maxItems']} items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path} items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                validate_schema_value(item, item_schema, root_schema, f"{path}.{index}", errors)

    if isinstance(value, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}.{key} is required")
        if isinstance(properties, dict):
            for key, child in value.items():
                if key in properties and isinstance(properties[key], dict):
                    validate_schema_value(child, properties[key], root_schema, f"{path}.{key}", errors)
                elif schema.get("additionalProperties") is False:
                    errors.append(f"{path}.{key} is not allowed")
                elif isinstance(schema.get("additionalProperties"), dict):
                    validate_schema_value(
                        child,
                        schema["additionalProperties"],
                        root_schema,
                        f"{path}.{key}",
                        errors,
                    )


def load_schema(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON schema object")
    return value


def validate_url_host(value: Any, *, host: str, label: str, errors: list[str]) -> None:
    if not isinstance(value, str):
        return
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.hostname != host:
        errors.append(f"{label} must use https://{host}")


def measurement_queries(rows: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(rows, list):
        return []
    queries: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        query = normalized_query(row.get("query"))
        queries.append(query)
        first_page = row.get("first_page")
        absolute_position = row.get("absolute_position")
        organic_position = row.get("organic_position")
        if first_page is False and (absolute_position is not None or organic_position is not None):
            errors.append(f"{label} absent results must use null absolute and organic positions")
    if len(queries) != len(set(queries)):
        errors.append(f"{label} queries must be unique after normalization")
    return queries


def validate_cross_artifact_invariants(baseline: dict[str, Any], experiment: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    baseline_app = baseline.get("app", {})
    experiment_app = experiment.get("app", {})
    if isinstance(baseline_app, dict) and isinstance(experiment_app, dict) and baseline_app != experiment_app:
        errors.append("experiment.app must exactly match baseline.app")

    baseline_source = baseline.get("source", {})
    if isinstance(baseline_app, dict) and isinstance(baseline_source, dict):
        partner_id = baseline_app.get("shopify_partner_id")
        numeric_app_id = baseline_app.get("shopify_app_numeric_id")
        if isinstance(partner_id, str) and partner_id.isdecimal() and isinstance(numeric_app_id, str):
            expected_entry_url = (
                f"https://partners.shopify.com/{partner_id}/apps/"
                f"{numeric_app_id}/distribution/app-store"
            )
            if baseline_source.get("entry_url") != expected_entry_url:
                errors.append("baseline.source.entry_url must match the Partner Admin URL derived from app metadata")
        validate_url_host(
            baseline_source.get("entry_url"),
            host="partners.shopify.com",
            label="baseline.source.entry_url",
            errors=errors,
        )
        validate_url_host(
            baseline_source.get("editor_url"),
            host="partners.shopify.com",
            label="baseline.source.editor_url",
            errors=errors,
        )
        validate_url_host(
            baseline_source.get("public_listing_url"),
            host="apps.shopify.com",
            label="baseline.source.public_listing_url",
            errors=errors,
        )

    for path in walk_keys(baseline) + walk_keys(experiment):
        lowered = path.lower()
        if any(part in lowered for part in FORBIDDEN_KEY_PARTS):
            errors.append(f"sensitive field is forbidden: {path}")

    excluded = baseline.get("excluded", [])
    exclusion_text = " ".join(str(item).lower() for item in excluded) if isinstance(excluded, list) else ""
    for alternatives in REQUIRED_EXCLUSION_CONCEPTS:
        if not any(concept in exclusion_text for concept in alternatives):
            errors.append(f"baseline.excluded must mention one of: {', '.join(alternatives)}")

    change = experiment.get("change", {})
    if isinstance(change, dict):
        field = str(change.get("field") or "")
        if (
            field.startswith("app_name")
            or field.startswith("app_card_subtitle")
            or field.startswith("app_store_search_terms")
        ):
            errors.append(
                "same-run experiments cannot use app name, app-card subtitle, or hidden search terms"
            )
        try:
            baseline_value = value_at(baseline.get("listing", {}), field)
        except (KeyError, IndexError, ValueError, TypeError):
            errors.append("experiment.change.field does not resolve inside baseline.listing")
        else:
            if not json_equal(change.get("original"), baseline_value):
                errors.append("experiment.change.original must exactly match the baseline field")
        if json_equal(change.get("variant"), change.get("original")):
            errors.append("experiment.change.variant must differ from original")
        limit = change.get("character_limit")
        variant = change.get("variant")
        if isinstance(limit, int) and not isinstance(limit, bool) and isinstance(variant, str) and len(variant) > limit:
            errors.append("experiment.change.variant exceeds character_limit")

    traffic_quality = experiment.get("traffic_quality", {})
    if isinstance(traffic_quality, dict):
        status = traffic_quality.get("status")
        clusters = traffic_quality.get("suspicious_clusters", [])
        sensitivity = traffic_quality.get("sensitivity", {})
        if status != "stable":
            errors.append("a live experiment artifact requires stable traffic-quality selection")
        if isinstance(clusters, list) and clusters:
            if not isinstance(sensitivity, dict) or sensitivity.get("performed") is not True:
                errors.append("suspicious traffic clusters require a performed sensitivity analysis")
        if isinstance(sensitivity, dict) and sensitivity.get("performed") is True:
            if not normalized_query(sensitivity.get("filter_description")):
                errors.append("performed sensitivity requires a filter_description")
            for field in ("target_changed", "guardrails_changed", "dominance_changed"):
                if not isinstance(sensitivity.get(field), bool):
                    errors.append(f"performed sensitivity requires boolean {field}")
            changed = any(sensitivity.get(field) is True for field in ("target_changed", "guardrails_changed", "dominance_changed"))
            if changed and status != "unstable":
                errors.append("changed sensitivity decisions require traffic_quality.status=unstable")
            if not changed and status == "unstable":
                errors.append("traffic_quality.status=unstable requires a changed sensitivity decision")

    measurement = experiment.get("measurement", {})
    expected_queries: list[str] = []
    before_queries: list[str] = []
    after_queries: list[str] = []
    if isinstance(measurement, dict):
        terms = measurement.get("terms", [])
        if isinstance(terms, list):
            expected_queries = [normalized_query(item.get("query")) for item in terms if isinstance(item, dict)]
            if len(expected_queries) != len(terms) or any(not query for query in expected_queries):
                errors.append("every measurement term needs a non-empty query")
            if len(expected_queries) != len(set(expected_queries)):
                errors.append("measurement terms must be unique after normalization")
            roles = [item.get("role") for item in terms if isinstance(item, dict)]
            if roles.count("target") != 1:
                errors.append("measurement terms must contain exactly one target")
            limit = measurement.get("per_phase_query_limit")
            if isinstance(limit, int) and not isinstance(limit, bool) and len(terms) > limit:
                errors.append("measurement term count exceeds per_phase_query_limit")
            target_queries = [
                normalized_query(item.get("query"))
                for item in terms
                if isinstance(item, dict) and item.get("role") == "target"
            ]
            historical_target = experiment.get("historical_analysis", {}).get("target", {})
            historical_term = normalized_query(historical_target.get("term")) if isinstance(historical_target, dict) else ""
            if len(target_queries) == 1 and target_queries[0] != historical_term:
                errors.append("measurement target must match historical_analysis.target.term")
        before_queries = measurement_queries(measurement.get("before"), "measurement.before", errors)
        after_queries = measurement_queries(measurement.get("after"), "measurement.after", errors)
        if sorted(before_queries) != sorted(expected_queries):
            errors.append("measurement.before must contain exactly one row for every selected term")

    publication = experiment.get("publication", {})
    publication_state = publication.get("state") if isinstance(publication, dict) else None
    classification = experiment.get("decision", {}).get("classification") if isinstance(experiment.get("decision"), dict) else None
    if isinstance(publication, dict):
        if publication_state == "public_verified":
            if publication.get("admin_variant_verified") is not True:
                errors.append("public_verified publication requires admin variant verification")
            if publication.get("matches_variant_exactly") is not True:
                errors.append("public_verified publication must exactly match the variant")
            if not json_equal(publication.get("public_value"), change.get("variant") if isinstance(change, dict) else None):
                errors.append("publication.public_value must exactly match change.variant")
            if classification != "inconclusive" and sorted(after_queries) != sorted(expected_queries):
                errors.append("complete decisions require one after measurement for every selected term")
            if classification == "inconclusive" and not set(after_queries).issubset(set(expected_queries)):
                errors.append("inconclusive after measurements may only contain selected terms")
        else:
            if after_queries:
                errors.append("after-search measurements are forbidden before public variant verification")
            if classification != "inconclusive":
                errors.append("a variant that was not publicly verified must be inconclusive")

    allowed_status_by_classification = {
        "favorable": "favorable_restored",
        "mixed": "mixed_restored",
        "unfavorable": "unfavorable_restored",
        "inconclusive": "inconclusive_restored",
    }
    expected_status = allowed_status_by_classification.get(classification)
    if expected_status and experiment.get("status") != expected_status:
        errors.append("experiment.status must match decision.classification and restored state")

    restoration = experiment.get("restoration", {})
    if isinstance(restoration, dict) and isinstance(change, dict):
        if not json_equal(restoration.get("restored_value"), change.get("original")):
            errors.append("restoration.restored_value must exactly match change.original")
        if not json_equal(restoration.get("public_value"), change.get("original")):
            errors.append("restoration.public_value must exactly match change.original")

    return errors


def validate(baseline: dict[str, Any], experiment: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    baseline_schema = load_schema(BASELINE_SCHEMA_PATH)
    experiment_schema = load_schema(EXPERIMENT_SCHEMA_PATH)
    validate_schema_value(baseline, baseline_schema, baseline_schema, "baseline", errors)
    validate_schema_value(experiment, experiment_schema, experiment_schema, "experiment", errors)
    errors.extend(validate_cross_artifact_invariants(baseline, experiment))
    return errors


def measurement_row(query: str, measured_at: str, absolute: int, organic: int, ads: int) -> dict[str, Any]:
    return {
        "query": query,
        "measured_at": measured_at,
        "search_id": None,
        "absolute_position": absolute,
        "organic_position": organic,
        "ads_before_app": ads,
        "first_page": True,
    }


def valid_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    app = {
        "fusionmetrics_app_key": "app-example-123456",
        "shopify_app_gid": "gid://partners/App/123456",
        "shopify_app_numeric_id": "123456",
        "shopify_partner_id": "1491902",
        "name": "Example",
        "locale": "en",
    }
    listing = {
        "app_name": "Example Audience Sync",
        "primary_category": "Marketing and conversion",
        "introduction": "Keep useful audience segments in sync.",
        "app_details": "Sync relevant store segments with supported marketing platforms.",
        "features": [
            "Sync selected customer segments",
            "Review audience health",
            "Control each destination",
        ],
        "app_card_subtitle": "Keep marketing audiences current",
        "app_store_search_terms": ["audience sync", "customer segments"],
        "web_search_title": "Example Audience Sync",
        "web_search_description": "Sync store segments with marketing platforms.",
        "media_alt_texts": ["Audience destination status"],
    }
    baseline = {
        "schema_version": SKILL_VERSION,
        "skill_version": SKILL_VERSION,
        "captured_at": "2026-08-23T10:00:00Z",
        "app": copy.deepcopy(app),
        "source": {
            "surface": "Shopify Partner Admin listing editor",
            "entry_url": "https://partners.shopify.com/1491902/apps/123456/distribution/app-store",
            "editor_url": "https://partners.shopify.com/1491902/apps/123456/distribution/app-store/listings/en",
            "public_listing_url": "https://apps.shopify.com/example-audience-sync",
            "status": "Published",
            "primary": True,
        },
        "listing": listing,
        "excluded": [
            "Tracking and analytics secrets",
            "Credentials, passwords, and test accounts",
            "Support contacts and reviewer instructions",
            "Cookies and browser storage",
        ],
    }
    experiment = {
        "schema_version": SKILL_VERSION,
        "skill_version": SKILL_VERSION,
        "experiment_id": "fixture-v1-1",
        "status": "favorable_restored",
        "app": copy.deepcopy(app),
        "sources": {
            "historical": "Fusion Metrics MCP",
            "live_rank": "Live Shopify App Store search",
            "listing": "Shopify Partner Admin listing editor",
        },
        "historical_analysis": {
            "span": {"first_date": "2025-01-01", "last_date": "2026-08-22"},
            "dataset_generated_at": "2026-08-23T09:00:00Z",
            "target": {
                "term": "facebook audience",
                "rationale": "Relevant term with stable downstream evidence and rank headroom.",
                "evidence_summary": "Traffic, click, and revenue evidence survive sensitivity analysis.",
            },
            "alternatives": ["audience sync"],
            "protected_terms": ["example", "audience sync"],
            "limitations": ["Live measurements are directional."],
        },
        "traffic_quality": {
            "assessed_at": "2026-08-23T09:10:00Z",
            "status": "stable",
            "dimensions_available": [
                "country",
                "date",
                "surface",
                "search_term",
                "click",
                "revenue",
                "historical_rank",
            ],
            "bot_classification_available": False,
            "suspicious_clusters": [
                {
                    "id": "sg-2026-surface-cluster",
                    "classification": "suspected",
                    "country": "Singapore",
                    "first_date": "2026-05-01",
                    "last_date": "2026-08-10",
                    "surface_type": "<none>",
                    "evidence": ["Raw listing views increased without comparable search-attributed activity."],
                }
            ],
            "sensitivity": {
                "performed": True,
                "filter_description": "Remove only Singapore rows from 2026-05-01 through 2026-08-10 with missing surface metadata.",
                "target_changed": False,
                "guardrails_changed": False,
                "dominance_changed": False,
                "max_traffic_share_change_pp": 0.15,
                "max_recency_lift_change_pp": 0.84,
                "conclusion": "The target and protected terms remain stable.",
            },
            "blanket_country_exclusion_applied": False,
            "limitations": ["No authoritative bot classification is exposed."],
        },
        "hypothesis": "A relevant exact search term improves target organic rank without harming protected terms.",
        "change": {
            "field": "introduction",
            "original": "Keep useful audience segments in sync.",
            "variant": "Sync store segments to relevant Facebook audiences.",
            "character_limit": 100,
        },
        "publication": {
            "state": "public_verified",
            "admin_variant_verified": True,
            "checked_at": "2026-08-23T10:03:00Z",
            "public_value": "Sync store segments to relevant Facebook audiences.",
            "matches_variant_exactly": True,
            "note": "The public English listing displayed the exact variant.",
        },
        "measurement": {
            "per_phase_query_limit": 2,
            "terms": [
                {"query": "facebook audience", "role": "target"},
                {"query": "example", "role": "brand_guardrail"},
            ],
            "before": [
                measurement_row("facebook audience", "2026-08-23T10:01:00Z", 12, 11, 1),
                measurement_row("example", "2026-08-23T10:01:30Z", 1, 1, 0),
            ],
            "after": [
                measurement_row("facebook audience", "2026-08-23T10:04:00Z", 9, 8, 1),
                measurement_row("example", "2026-08-23T10:04:30Z", 1, 1, 0),
            ],
        },
        "decision": {
            "classification": "favorable",
            "reason": "The target improved while the brand guardrail remained stable.",
            "directional_only": True,
        },
        "restoration": {
            "performed": True,
            "admin_verified_at": "2026-08-23T10:05:00Z",
            "restored_value": "Keep useful audience segments in sync.",
            "admin_matches_original_exactly": True,
            "public_verified_at": "2026-08-23T10:06:00Z",
            "public_value": "Keep useful audience segments in sync.",
            "public_matches_original_exactly": True,
        },
    }
    return baseline, experiment


def self_test() -> int:
    baseline, experiment = valid_fixture()
    valid_errors = validate(baseline, experiment)
    if valid_errors:
        print("self-test failed: valid fixture was rejected", file=sys.stderr)
        for error in valid_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    cases: list[tuple[str, dict[str, Any], dict[str, Any]]] = []

    missing_app_name = copy.deepcopy(baseline)
    del missing_app_name["app"]["name"]
    cases.append(("missing schema-required app name", missing_app_name, copy.deepcopy(experiment)))

    invalid_measurement = copy.deepcopy(experiment)
    invalid_measurement["measurement"]["before"][0]["measured_at"] = "not-a-date"
    invalid_measurement["measurement"]["before"][0]["organic_position"] = 0
    cases.append(("invalid measurement values", copy.deepcopy(baseline), invalid_measurement))

    contradictory_status = copy.deepcopy(experiment)
    contradictory_status["decision"]["classification"] = "unfavorable"
    cases.append(("contradictory status", copy.deepcopy(baseline), contradictory_status))

    unstable_traffic = copy.deepcopy(experiment)
    unstable_traffic["traffic_quality"]["status"] = "unstable"
    unstable_traffic["traffic_quality"]["sensitivity"]["target_changed"] = True
    cases.append(("unstable traffic quality", copy.deepcopy(baseline), unstable_traffic))

    subtitle_change = copy.deepcopy(experiment)
    subtitle_change["change"] = {
        "field": "app_card_subtitle",
        "original": baseline["listing"]["app_card_subtitle"],
        "variant": "Facebook audience sync",
        "character_limit": 62,
    }
    cases.append(("subtitle keyword experiment", copy.deepcopy(baseline), subtitle_change))

    hidden_search_term_change = copy.deepcopy(experiment)
    hidden_search_term_change["change"] = {
        "field": "app_store_search_terms.0",
        "original": baseline["listing"]["app_store_search_terms"][0],
        "variant": "facebook audience",
        "character_limit": 20,
    }
    cases.append(("hidden search-term experiment", copy.deepcopy(baseline), hidden_search_term_change))

    unpublished_after_search = copy.deepcopy(experiment)
    unpublished_after_search["publication"].update(
        {
            "state": "pending_review",
            "public_value": "audience sync",
            "matches_variant_exactly": False,
        }
    )
    cases.append(("after search without publication", copy.deepcopy(baseline), unpublished_after_search))

    broken_restoration = copy.deepcopy(experiment)
    broken_restoration["restoration"]["public_matches_original_exactly"] = False
    cases.append(("broken public restoration", copy.deepcopy(baseline), broken_restoration))

    blanket_country_filter = copy.deepcopy(experiment)
    blanket_country_filter["traffic_quality"]["blanket_country_exclusion_applied"] = True
    cases.append(("blanket country exclusion", copy.deepcopy(baseline), blanket_country_filter))

    for label, candidate_baseline, candidate_experiment in cases:
        if not validate(candidate_baseline, candidate_experiment):
            print(f"self-test failed: {label} was accepted", file=sys.stderr)
            return 1

    print(f"self-test passed ({len(cases) + 1} cases)")
    return 0


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--experiment", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.baseline or not args.experiment:
        parser.error("--baseline and --experiment are required unless --self-test is used")
    try:
        errors = validate(load_json(args.baseline), load_json(args.experiment))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"validation failed: {error}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("artifacts valid for skill 1.1.0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
