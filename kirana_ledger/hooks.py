from . import __version__ as app_version

app_name = "kirana_ledger"
app_title = "Kirana Ledger"
app_publisher = "Kirana Tech"
app_description = "Hyper-Local Inventory + Udhaar (Credit) Ledger for Kirana Shops"
app_email = "dev@kirana-ledger.example.com"
app_license = "MIT"

# ─── Fixtures (synced on install/update) ────────────────────────
fixtures = [
    {"dt": "Udhaar Customer", "filters": []},
    {"dt": "Udhaar Entry", "filters": []},
    {"dt": "Quick Inventory Item", "filters": []},
    {"dt": "Workspace", "filters": [["module", "=", "Kirana Ledger"]]},
]

# ─── Doc Events (server-side hooks) ────────────────────────────
doc_events = {
    "Udhaar Entry": {
        "on_update": "kirana_ledger.kirana_ledger.api.check_credit_limit",
    }
}

# ─── Patch list ─────────────────────────────────────────────────
patches = [
    "kirana_ledger.patches.add_demo_data",
]
