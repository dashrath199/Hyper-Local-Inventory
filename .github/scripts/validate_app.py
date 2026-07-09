#!/usr/bin/env python3
"""Validate a Frappe/ERPNext custom app structure.

Checks:
  - Directory structure matches Frappe conventions
  - DocType JSON files have required fields
  - Report JSON files have required fields
  - Workspace JSON has required fields
  - Notification JSON has required fields
  - hooks.py is syntactically valid
  - Demo data fixture records reference valid DocTypes
"""

import json
import os
import sys
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
errors = []
warnings = []


def error(msg):
    errors.append(msg)
    print(f"  [ERROR] {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  [WARN] {msg}")


def ok(msg):
    print(f"  [OK] {msg}")


# ── Required DocType fields ──────────────────────────────────
REQUIRED_DOCTYPE_FIELDS = [
    "doctype", "name", "module", "fields", "permissions",
]
REQUIRED_FIELD_KEYS = [
    "fieldname", "fieldtype", "label",
]
OPTIONAL_REPORT_DOCTYPES = {"Report"}


def check_doctype(json_path: str, data: dict):
    """Validate a single DocType JSON file."""
    name = data.get("name", os.path.basename(os.path.dirname(json_path)))

    for field in REQUIRED_DOCTYPE_FIELDS:
        if field not in data:
            error(f"{name}: missing required field '{field}'")

    fields = data.get("fields", [])
    if not fields:
        error(f"{name}: DocType has no fields defined")
    else:
        for i, f in enumerate(fields):
            # Layout fields (Column Break, Section Break, Tab Break) don't need labels
            skip_label = f.get("fieldtype") in ("Column Break", "Section Break", "Tab Break")
            for key in REQUIRED_FIELD_KEYS:
                if key == "label" and skip_label:
                    continue
                if key not in f:
                    error(f"{name}: field #{i} ('{f.get('fieldname', '?')}') missing '{key}'")

    permissions = data.get("permissions", [])
    if not permissions:
        warn(f"{name}: no permissions defined — app may not be usable")

    # Check for required Frappe DocType metadata
    if "engine" not in data:
        warn(f"{name}: missing 'engine' (defaults to InnoDB, but explicit is better)")
    if "modified" not in data:
        warn(f"{name}: missing 'modified' timestamp")


def check_report(json_path: str, data: dict):
    """Validate a Report JSON file."""
    name = data.get("name", os.path.basename(os.path.dirname(json_path)))

    if data.get("doctype") not in OPTIONAL_REPORT_DOCTYPES:
        warn(f"{name}: 'doctype' should be 'Report' (got '{data.get('doctype')}')")
    if not data.get("query"):
        error(f"{name}: report has no SQL query")
    if not data.get("ref_doctype"):
        error(f"{name}: report has no ref_doctype")


def check_workspace(json_path: str, data: dict):
    """Validate a Workspace JSON file."""
    name = data.get("name", os.path.basename(os.path.dirname(json_path)))

    if not data.get("label"):
        error(f"{name}: workspace has no label")
    if not data.get("module"):
        error(f"{name}: workspace has no module")
    if not data.get("content") and not data.get("shortcuts"):
        warn(f"{name}: workspace has no content or shortcuts — will be empty")


def check_notification(json_path: str, data: dict):
    """Validate a Notification JSON file."""
    name = data.get("name", os.path.basename(os.path.dirname(json_path)))

    if not data.get("document_type"):
        error(f"{name}: notification has no document_type")
    if not data.get("event"):
        error(f"{name}: notification has no event trigger")
    if not data.get("subject"):
        error(f"{name}: notification has no subject")
    if not data.get("recipients"):
        error(f"{name}: notification has no recipients")
    if not data.get("channel"):
        warn(f"{name}: notification has no channel (defaults to Email)")


def validate_json_file(filepath: str):
    """Load and validate a JSON file based on its directory context."""
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        error(f"{filepath}: invalid JSON — {e}")
        return
    except FileNotFoundError:
        error(f"{filepath}: file not found")
        return

    # Determine type from directory structure
    # For a file at .../doctype/udhaar_customer/udhaar_customer.json,
    # the grandparent directory is "doctype", the parent is "udhaar_customer".
    grandparent = os.path.basename(os.path.dirname(os.path.dirname(filepath)))

    if grandparent == "doctype":
        check_doctype(filepath, data)
    elif grandparent == "report":
        check_report(filepath, data)
    elif grandparent == "workspace":
        check_workspace(filepath, data)
    elif grandparent == "notification":
        check_notification(filepath, data)
    else:
        # Generic JSON — just validate it parses
        pass


def validate_directory_structure():
    """Check that the Frappe app directory structure is correct."""
    print("\n--- Checking directory structure...")

    mandatory_dirs = [
        "kirana_ledger/doctype",
        "kirana_ledger/report",
        "kirana_ledger/workspace",
        "kirana_ledger/notification",
        "kirana_ledger/patches",
        "kirana_ledger/fixtures",
    ]

    for d in mandatory_dirs:
        full_path = os.path.join(ROOT, d)
        if os.path.isdir(full_path):
            ok(f"Found {d}/")
        else:
            warn(f"Missing directory: {d}/")

    # Check each doctype has __init__.py
    doctype_dir = os.path.join(ROOT, "kirana_ledger/doctype")
    if os.path.isdir(doctype_dir):
        for dt in os.listdir(doctype_dir):
            dt_path = os.path.join(doctype_dir, dt)
            if os.path.isdir(dt_path):
                init_file = os.path.join(dt_path, "__init__.py")
                json_file = os.path.join(dt_path, f"{dt}.json")
                py_file = os.path.join(dt_path, f"{dt}.py")

                if not os.path.exists(init_file):
                    warn(f"doctype/{dt}/ missing __init__.py")
                if not os.path.exists(json_file):
                    error(f"doctype/{dt}/ missing {dt}.json")
                if not os.path.exists(py_file):
                    warn(f"doctype/{dt}/ missing {dt}.py")


def validate_fixtures():
    """Validate that fixture JSON records reference existing DocTypes."""
    fixtures_dir = os.path.join(ROOT, "kirana_ledger/fixtures")
    if not os.path.isdir(fixtures_dir):
        return

    print("\n--- Checking fixtures...")

    # Collect known DocTypes from the doctype directory
    doctype_dir = os.path.join(ROOT, "kirana_ledger/doctype")
    known_doctypes = set()
    if os.path.isdir(doctype_dir):
        for dt in os.listdir(doctype_dir):
            dt_path = os.path.join(doctype_dir, dt)
            if os.path.isdir(dt_path):
                json_file = os.path.join(dt_path, f"{dt}.json")
                if os.path.exists(json_file):
                    with open(json_file, encoding="utf-8") as f:
                        data = json.load(f)
                        known_doctypes.add(data.get("name", dt))
                known_doctypes.add(dt.replace("_", " ").title())

    for fname in os.listdir(fixtures_dir):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(fixtures_dir, fname)
        try:
            with open(fpath, encoding="utf-8") as f:
                records = json.load(f)
        except json.JSONDecodeError:
            error(f"fixtures/{fname}: invalid JSON")
            continue

        if not isinstance(records, list):
            error(f"fixtures/{fname}: should be a JSON array")
            continue

        for i, record in enumerate(records):
            doctype = record.get("doctype")
            if not doctype:
                error(f"fixtures/{fname}[{i}]: missing 'doctype' field")
            elif doctype not in known_doctypes:
                warn(f"fixtures/{fname}[{i}]: '{doctype}' not in known DocTypes")

        ok(f"fixtures/{fname}: {len(records)} records")


def validate_hooks():
    """Check that hooks.py is syntactically valid."""
    print("\n--- Checking hooks.py...")
    hooks_path = os.path.join(ROOT, "kirana_ledger/hooks.py")
    if not os.path.exists(hooks_path):
        error("kirana_ledger/hooks.py not found")
        return

    try:
        compile(open(hooks_path, encoding="utf-8").read(), hooks_path, "exec")
        ok("hooks.py compiles")
    except SyntaxError as e:
        error(f"hooks.py has syntax errors: {e}")


def main():
    print("=" * 50)
    print("  Kirana Ledger — App Structure Validation")
    print("=" * 50)

    validate_directory_structure()
    validate_hooks()

    # Walk all JSON files
    print("\n--- Checking JSON files...")
    json_count = 0
    for root, dirs, files in os.walk(ROOT):
        # Skip .git directory
        if ".git" in root:
            continue
        for fname in files:
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(root, fname)
            validate_json_file(fpath)
            json_count += 1

    validate_fixtures()

    # Summary
    print(f"\n{'=' * 50}")
    print(f"  Summary: {json_count} JSON files checked")
    if errors:
        print(f"  [ERROR] {len(errors)} errors found:")
        for e in errors:
            print(f"    - {e}")
    if warnings:
        print(f"  [WARN] {len(warnings)} warnings:")
        for w in warnings:
            print(f"    - {w}")
    if not errors and not warnings:
        print("  [OK] All checks passed - app structure looks good!")
    elif not errors:
        print("  [WARN] No errors, but review warnings above")
    print(f"{'=' * 50}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
