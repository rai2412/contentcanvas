"""
OpenAPI Description Patcher
Reads a filled-in audit CSV and patches the descriptions back into the JSON spec.

Usage:
    python patch_spec.py audit_report.csv original_spec.json

Output:
    original_spec_patched.json (new file — original is never modified)
"""

import json
import csv
import sys
from pathlib import Path


def load_spec(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def load_csv(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader if row.get("suggested_description", "").strip()]


def parse_location(location):
    """Parse 'GET /audit/{accountId}' into ('get', '/audit/{accountId}')."""
    parts = location.split(" ", 1)
    if len(parts) == 2:
        return parts[0].lower(), parts[1]
    return None, None


def patch_operations(spec, rows):
    """Patch operation summaries and descriptions."""
    patched = 0
    for row in rows:
        if row["gap_type"] not in ("operation_summary", "operation_description"):
            continue

        method, path = parse_location(row["location"])
        if not method or not path:
            continue

        operation = spec.get("paths", {}).get(path, {}).get(method)
        if not operation:
            print(f"  WARNING: endpoint not found: {method.upper()} {path}")
            continue

        field = row["field"]  # "summary" or "description"
        operation[field] = row["suggested_description"]
        patched += 1

    return patched


def patch_parameters(spec, rows):
    """Patch parameter descriptions."""
    patched = 0
    for row in rows:
        if row["gap_type"] != "parameter_description":
            continue

        method, path = parse_location(row["location"])
        if not method or not path:
            continue

        operation = spec.get("paths", {}).get(path, {}).get(method)
        if not operation:
            print(f"  WARNING: endpoint not found: {method.upper()} {path}")
            continue

        param_name = row["field"]
        for param in operation.get("parameters", []):
            if param["name"] == param_name:
                param["description"] = row["suggested_description"]
                patched += 1
                break
        else:
            print(f"  WARNING: param not found: {param_name} on {method.upper()} {path}")

    return patched


def patch_responses(spec, rows):
    """Patch response descriptions."""
    patched = 0
    for row in rows:
        if row["gap_type"] != "response_description":
            continue

        method, path = parse_location(row["location"])
        if not method or not path:
            continue

        operation = spec.get("paths", {}).get(path, {}).get(method)
        if not operation:
            print(f"  WARNING: endpoint not found: {method.upper()} {path}")
            continue

        # field is "response 200", "response 400", etc.
        status_code = row["field"].replace("response ", "")
        response = operation.get("responses", {}).get(status_code)
        if response:
            response["description"] = row["suggested_description"]
            patched += 1
        else:
            print(f"  WARNING: response {status_code} not found on {method.upper()} {path}")

    return patched


def patch_schema_properties(spec, rows):
    """Patch schema property descriptions."""
    patched = 0
    schemas = spec.get("components", {}).get("schemas", {})

    for row in rows:
        if row["gap_type"] != "schema_property":
            continue

        schema_name = row["location"]
        prop_name = row["field"]

        schema = schemas.get(schema_name)
        if not schema:
            print(f"  WARNING: schema not found: {schema_name}")
            continue

        prop = schema.get("properties", {}).get(prop_name)
        if prop:
            prop["description"] = row["suggested_description"]
            patched += 1
        else:
            print(f"  WARNING: property not found: {prop_name} in {schema_name}")

    return patched


def main():
    if len(sys.argv) < 3:
        print("Usage: python patch_spec.py audit_report.csv original_spec.json")
        sys.exit(1)

    csv_path = sys.argv[1]
    spec_path = sys.argv[2]

    # Load
    spec = load_spec(spec_path)
    rows = load_csv(csv_path)

    print(f"Loaded {len(rows)} filled descriptions from {csv_path}\n")

    if not rows:
        print("No filled descriptions found. Fill in the 'suggested_description' column first.")
        sys.exit(0)

    # Patch each type
    counts = {}
    counts["operations"] = patch_operations(spec, rows)
    counts["parameters"] = patch_parameters(spec, rows)
    counts["responses"] = patch_responses(spec, rows)
    counts["schema_properties"] = patch_schema_properties(spec, rows)

    # Save patched spec
    output_path = Path(spec_path).stem + "_patched.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    # Summary
    total = sum(counts.values())
    print("=" * 50)
    print("PATCH SUMMARY")
    print("=" * 50)
    for category, count in counts.items():
        print(f"  {category}: {count}")
    print(f"\n  TOTAL PATCHED: {total}")
    print("=" * 50)
    print(f"\nPatched spec saved to: {output_path}")
    print("Original file was NOT modified.")


if __name__ == "__main__":
    main()
