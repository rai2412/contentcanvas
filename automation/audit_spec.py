"""
OpenAPI Documentation Gap Auditor
Parses an OpenAPI spec and outputs a CSV report of all missing descriptions.
Open the CSV in Excel or Google Sheets, fill in the 'suggested_description' column.

Usage:
    python audit_spec.py your_openapi_spec.json
"""

import json
import csv
import sys
from pathlib import Path


def load_spec(filepath):
    """Load OpenAPI spec from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def is_empty(value):
    """Check if a description is missing or empty."""
    return value is None or str(value).strip() == ""


def audit_operations(spec):
    """Find operations with missing summaries or descriptions."""
    gaps = []
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        for method, operation in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                tags = ", ".join(operation.get("tags", []))

                if is_empty(operation.get("summary")):
                    gaps.append({
                        "gap_type": "operation_summary",
                        "location": f"{method.upper()} {path}",
                        "field": "summary",
                        "parent": tags,
                        "data_type": "",
                        "required": "",
                        "existing_text": operation.get("description", "")[:150],
                        "suggested_description": "",
                    })

                if is_empty(operation.get("description")):
                    gaps.append({
                        "gap_type": "operation_description",
                        "location": f"{method.upper()} {path}",
                        "field": "description",
                        "parent": tags,
                        "data_type": "",
                        "required": "",
                        "existing_text": operation.get("summary", ""),
                        "suggested_description": "",
                    })
    return gaps


def audit_parameters(spec):
    """Find parameters with missing descriptions."""
    gaps = []
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        for method, operation in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                params = operation.get("parameters", [])

                for param in params:
                    if is_empty(param.get("description")):
                        gaps.append({
                            "gap_type": "parameter_description",
                            "location": f"{method.upper()} {path}",
                            "field": param["name"],
                            "parent": f"param ({param.get('in', '')})",
                            "data_type": param.get("schema", {}).get("type", ""),
                            "required": "yes" if param.get("required") else "no",
                            "existing_text": "",
                            "suggested_description": "",
                        })
    return gaps


def audit_responses(spec):
    """Find responses with missing or empty descriptions."""
    gaps = []
    paths = spec.get("paths", {})

    for path, methods in paths.items():
        for method, operation in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                responses = operation.get("responses", {})

                for status_code, response in responses.items():
                    if is_empty(response.get("description")):
                        gaps.append({
                            "gap_type": "response_description",
                            "location": f"{method.upper()} {path}",
                            "field": f"response {status_code}",
                            "parent": operation.get("summary", ""),
                            "data_type": "",
                            "required": "",
                            "existing_text": "",
                            "suggested_description": "",
                        })
    return gaps


def audit_schema_properties(spec):
    """Find schema properties with missing descriptions."""
    gaps = []
    schemas = spec.get("components", {}).get("schemas", {})

    for schema_name, schema in schemas.items():
        properties = schema.get("properties", {})
        required_fields = schema.get("required", [])

        for prop_name, prop in properties.items():
            if is_empty(prop.get("description")):
                example = prop.get("example", "")
                if example:
                    example = str(example)[:100]

                gaps.append({
                    "gap_type": "schema_property",
                    "location": schema_name,
                    "field": prop_name,
                    "parent": "schema",
                    "data_type": prop.get("type", ""),
                    "required": "yes" if prop_name in required_fields else "no",
                    "existing_text": example,
                    "suggested_description": "",
                })
    return gaps


def run_audit(spec_path):
    """Run the complete audit and return all gaps."""
    spec = load_spec(spec_path)

    all_gaps = []
    all_gaps.extend(audit_operations(spec))
    all_gaps.extend(audit_parameters(spec))
    all_gaps.extend(audit_responses(spec))
    all_gaps.extend(audit_schema_properties(spec))

    return all_gaps


def write_csv(gaps, output_path):
    """Write gaps to CSV."""
    fieldnames = [
        "gap_type",
        "location",
        "field",
        "parent",
        "data_type",
        "required",
        "existing_text",
        "suggested_description",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(gaps)


def print_summary(gaps):
    """Print a quick summary to the terminal."""
    by_type = {}
    for gap in gaps:
        t = gap["gap_type"]
        by_type[t] = by_type.get(t, 0) + 1

    print("=" * 50)
    print("AUDIT SUMMARY")
    print("=" * 50)
    for gap_type, count in by_type.items():
        print(f"  {gap_type}: {count}")
    print(f"\n  TOTAL GAPS: {len(gaps)}")
    print("=" * 50)


if __name__ == "__main__":
    spec_path = sys.argv[1] if len(sys.argv) > 1 else "sample_spec.json"
    gaps = run_audit(spec_path)

    # Output CSV
    output_path = Path(spec_path).stem + "_audit.csv"
    write_csv(gaps, output_path)

    print_summary(gaps)
    print(f"\nCSV saved to: {output_path}")
    print("Open in Excel or Google Sheets. Fill in the 'suggested_description' column.")
