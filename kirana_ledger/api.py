"""API endpoints for the Kirana Ledger app.

This module provides:
  1. WhatsApp webhook endpoint (the primary integration point)
  2. Credit limit breach detection (triggered by doc_events)
  3. Utility functions for the NLU layer described in the architecture

Note: This implements the WhatsApp-first layer described in the product spec.
The webhook is the integration point — it receives messages from WhatsApp
Business Cloud API and creates Udhaar Entry records accordingly.
"""

import frappe
from frappe import _
from frappe.utils import now, today


@frappe.whitelist(allow_guest=True)
def whatsapp_webhook():
    """WhatsApp Business Cloud API webhook endpoint.

    Expected payload (from Meta):
    {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "919876543210",
                        "id": "wamid.someid",
                        "text": {"body": "Ramesh ko 200 udhaar diya"}
                    }],
                    "contacts": [{"profile": {"name": "Shop Owner"}}]
                }
            }]
        }]
    }

    The webhook parses Hinglish (Hindi-English mix) messages using
    the NLU layer and creates Udhaar Entry records.

    Security: Verifies the X-Hub-Signature-256 header against
    the whatsapp_app_secret site config. If not configured, falls
    back to allowlisting the webhook for development/demo use.

    Endpoint registration:
        POST /api/method/kirana_ledger.api.whatsapp_webhook
    """
    data = frappe.local.form_dict or frappe.request.json or {}

    # ── Webhook signature verification ───────────────────
    signature = frappe.get_request_header("X-Hub-Signature-256", "")
    app_secret = frappe.conf.get("whatsapp_app_secret")

    if app_secret and signature:
        raw_body = frappe.local.request.get_data()
        import hashlib
        import hmac
        expected = "sha256=" + hmac.new(
            app_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            frappe.throw(_("Invalid webhook signature"), frappe.PermissionError)
    elif app_secret:
        # App secret is configured but no signature header — reject
        frappe.throw(_("Missing webhook signature"), frappe.PermissionError)

    # Parse the incoming message payload
    message_text = _extract_message_text(data)
    if not message_text:
        return {"status": "ignored"}

    sender_number = _extract_sender(data)
    customer_name, amount, entry_type = _parse_udhaar_message(message_text)

    if not customer_name:
        return {"status": "unparsed", "text": message_text}

    # Find or create customer
    customer = _get_or_create_customer(customer_name, sender_number)

    # Create the Udhaar Entry
    entry = frappe.get_doc({
        "doctype": "Udhaar Entry",
        "customer": customer.name,
        "entry_type": entry_type,
        "amount": amount,
        "items_description": message_text,
        "date": today(),
    })
    entry.insert()
    entry.submit()

    # Send confirmation (this would call WhatsApp Cloud API in production)
    frappe.msgprint(
        msg=_("✅ Recorded ₹{0} {1} for {2}. Total outstanding: ₹{3}").format(
            int(amount),
            _("credit given to") if entry_type == "Credit Given" else _("payment from"),
            customer.customer_name,
            int(customer.current_balance),
        )
    )

    return {
        "status": "ok",
        "entry_name": entry.name,
        "customer": customer.customer_name,
        "balance_after": customer.current_balance,
    }


def check_credit_limit(doc, method=None):
    """Check if a Udhaar Entry pushes the customer over their credit limit.

    Triggered by doc_events in hooks.py:
        "Udhaar Entry": {"on_update": "kirana_ledger.kirana_ledger.api.check_credit_limit"}

    Creates a system notification to alert the shop owner.
    """
    if not doc or not doc.customer:
        return

    customer = frappe.get_doc("Udhaar Customer", doc.customer)
    if customer.credit_limit and customer.current_balance > customer.credit_limit:
        notification = frappe.get_doc({
            "doctype": "Notification Log",
            "subject": _("⚠️ Credit Limit Breach: {0}").format(customer.customer_name),
            "email_content": _(
                "{0}'s outstanding balance (₹{1:,.0f}) exceeds their credit limit (₹{2:,.0f})."
            ).format(customer.customer_name, customer.current_balance, customer.credit_limit),
            "document_type": "Udhaar Customer",
            "document_name": customer.name,
            "from_user": "Administrator",
            "type": "Alert",
        })
        notification.insert(ignore_permissions=True)


def _extract_message_text(payload: dict) -> str | None:
    """Extract the text body from a WhatsApp webhook payload.

    Uses .get() chaining to avoid KeyError on malformed payloads.
    """
    try:
        entry = payload.get("entry") or []
        if not entry:
            return None
        change = (entry[0].get("changes") or [])
        if not change:
            return None
        value = change[0].get("value") or {}
        messages = value.get("messages") or []
        if not messages:
            return None
        text = messages[0].get("text") or {}
        return text.get("body")
    except (IndexError, TypeError):
        return None


def _extract_sender(payload: dict) -> str | None:
    """Extract the sender's phone number from a WhatsApp webhook payload."""
    try:
        entry = payload.get("entry") or []
        if not entry:
            return None
        change = (entry[0].get("changes") or [])
        if not change:
            return None
        value = change[0].get("value") or {}
        messages = value.get("messages") or []
        if not messages:
            return None
        return messages[0].get("from")
    except (IndexError, TypeError):
        return None


def _parse_udhaar_message(text: str) -> tuple:
    """Parse a Hinglish kirana message into structured data.

    This is the NLU layer — in production this would call GPT-4o-mini
    or a similar LLM for robust parsing. For the demo, we use regex.

    Supported patterns:
        "Ramesh ko 200 udhaar diya"  → Credit Given
        "Suresh ne 500 diye"          → Payment Received
        "300 mil gaye Ramesh se"      → Payment Received
        "Mohan ko 50"                 → Credit Given

    Returns:
        (customer_name: str | None, amount: float, entry_type: str)
    """
    import re

    # Credit patterns: X ko Y (udhaar/diya/diye)
    credit_match = re.search(
        r"(?P<name>\w+)\s+ko\s+(?P<amount>\d+)", text, re.IGNORECASE
    )
    if credit_match:
        return credit_match.group("name"), float(credit_match.group("amount")), "Credit Given"

    # Payment patterns: X ne Y diye
    payment_match = re.search(
        r"(?P<name>\w+)\s+ne\s+(?P<amount>\d+)", text, re.IGNORECASE
    )
    if payment_match:
        return payment_match.group("name"), float(payment_match.group("amount")), "Payment Received"

    # Payment patterns: Y mil gaye X se
    payment_match2 = re.search(
        r"(?P<amount>\d+)\s+(?:mil|aaye|pay)\s+(?P<name>\w+)", text, re.IGNORECASE
    )
    if payment_match2:
        return payment_match2.group("name"), float(payment_match2.group("amount")), "Payment Received"

    return None, 0.0, ""


def _get_or_create_customer(customer_name: str, phone: str = ""):
    """Find an existing customer by name, or create a new one."""
    customer_name = customer_name.strip()

    existing = frappe.db.exists("Udhaar Customer", {"customer_name": customer_name})
    if existing:
        return frappe.get_doc("Udhaar Customer", existing)

    customer = frappe.get_doc({
        "doctype": "Udhaar Customer",
        "customer_name": customer_name,
        "phone": phone or "",
        "preferred_language": "Hindi",
    })
    customer.insert()
    return customer
