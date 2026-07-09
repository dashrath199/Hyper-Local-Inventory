"""Patch to seed demo data for the portfolio demo.

This patch is registered in hooks.py:
    patches = ["kirana_ledger.patches.add_demo_data"]

It loads fixture data from fixtures/demo_data.json and creates
the corresponding DocType records.

The demo is scoped to work with the 'Shop Owner' role so that
anyone who installs this app can immediately explore the full
Udhaar Ledger workspace with realistic sample data.
"""

import json
import os

import frappe


def execute():
    """Seed demo data from the fixtures JSON file."""
    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "fixtures",
        "demo_data.json",
    )

    if not os.path.exists(fixture_path):
        frappe.log_error(
            message=f"Demo data fixture not found at {fixture_path}",
            title="Kirana Ledger: Demo data not loaded",
        )
        return

    with open(fixture_path) as f:
        records = json.load(f)

    for record in records:
        doctype = record.pop("doctype")
        name = record.pop("name", None)

        # Skip if record already exists
        if name and frappe.db.exists(doctype, name):
            continue

        doc = frappe.get_doc({"doctype": doctype, **record})
        doc.insert()

        # If the record was submitted (Udhaar Entries with docstatus=1)
        if record.get("docstatus") == 1:
            doc.submit()

    frappe.db.commit()
