# OpenAPI Documentation Gap Auditor

A Python script that parses an OpenAPI specification (JSON), detects all missing or empty descriptions, and outputs a CSV report you can open in Excel or Google Sheets to fill in manually.

## What it does

The script walks through every operation, parameter, response, and schema property in your OpenAPI spec and flags anything with a missing or empty `description` field. Each gap is logged with its location, type, and surrounding context so you can write the description without switching back to the spec.

### What it checks

| Check | What it flags |
|-------|--------------|
| Operation summaries | Endpoints with empty or missing `summary` |
| Operation descriptions | Endpoints with empty or missing `description` |
| Parameter descriptions | Path, query, and header parameters without `description` |
| Response descriptions | HTTP response codes (200, 400, 403, etc.) without `description` |
| Schema properties | Properties in `components/schemas` without `description` |

## Requirements

- Python 3.8+
- No external dependencies (uses only `json`, `csv`, `sys`, `pathlib` from the standard library)

## Usage

```bash
python audit_spec.py your_openapi_spec.json
```

### Output

1. **Terminal summary** showing gap counts by type
2. **CSV file** named `your_openapi_spec_audit.csv` in the current directory

### Example

```bash
$ python audit_spec.py thehive_api.json

==================================================
AUDIT SUMMARY
==================================================
  operation_summary: 3
  operation_description: 6
  parameter_description: 18
  response_description: 3
  schema_property: 44

  TOTAL GAPS: 74
==================================================

CSV saved to: thehive_api_audit.csv
Open in Excel or Google Sheets. Fill in the 'suggested_description' column.
```

## CSV columns

| Column | Purpose |
|--------|---------|
| `gap_type` | Category: `operation_summary`, `operation_description`, `parameter_description`, `response_description`, `schema_property` |
| `location` | Where the gap is: endpoint path (e.g. `GET /case/{caseId}`) or schema name (e.g. `InputCreateCase`) |
| `field` | The specific field that's missing a description (e.g. `summary`, `caseId`, `response 400`, `tlp`) |
| `parent` | Additional context: tags for operations, `param (path)` for parameters, `schema` for properties |
| `data_type` | The field's type (e.g. `string`, `integer`, `boolean`) — helps you write accurate descriptions |
| `required` | Whether the field is required (`yes`/`no`) |
| `existing_text` | Any neighbouring text that already exists (e.g. if summary is missing but description exists) |
| `suggested_description` | **Empty — you fill this in** |

## Workflow

1. Run the audit: `python audit_spec.py your_spec.json`
2. Open the CSV in Excel or Google Sheets
3. Sort by `gap_type` to batch your work (all parameters together, all schema properties together)
4. Fill in the `suggested_description` column
5. You can fill in some now and come back for the rest later — partial completion is fine

## Optional: Patch descriptions back into the spec

If you also have `patch_spec.py`, you can apply your filled-in descriptions back to the JSON spec:

```bash
python patch_spec.py your_spec_audit.csv your_spec.json
```

This creates `your_spec_patched.json` with your descriptions inserted. The original file is never modified.

## How it works

The script makes four passes through the spec:

1. **Operations pass**: Iterates over every path and HTTP method, checks for empty `summary` and `description`
2. **Parameters pass**: Checks every parameter across all endpoints for missing `description`
3. **Responses pass**: Checks every response code for empty `description`
4. **Schema properties pass**: Checks every property in every schema under `components/schemas` for missing `description`

Each gap is recorded with enough context (path, method, type, required status, existing text) that you can write the description directly in the spreadsheet without needing to refer back to the spec.

## Limitations

- Reads JSON specs only (convert YAML to JSON first with `yq` or similar)
- Does not follow `$ref` references — checks schemas defined directly under `components/schemas`
- Does not check `requestBody` descriptions (can be added if needed)
- Does not modify the original spec file
