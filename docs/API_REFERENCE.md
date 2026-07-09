# Kirana Ledger — API Reference

## WhatsApp Webhook

Parses natural language messages in Hinglish (Hindi-English mix) and creates Udhaar Entry records.

### Endpoint

```
POST /api/method/kirana_ledger.api.whatsapp_webhook
```

### Authentication

- **Development**: No authentication required (site config `whatsapp_app_secret` not set)
- **Production**: Requires `X-Hub-Signature-256` header verified against `whatsapp_app_secret` site config

### Request Format (from Meta WhatsApp Cloud API)

```json
{
  "entry": [
    {
      "changes": [
        {
          "value": {
            "messages": [
              {
                "from": "919876543210",
                "id": "wamid.HBgLOTE4MDc2NTQzMjEwVQ==",
                "timestamp": "1720512345",
                "text": {
                  "body": "Ramesh ko 200 udhaar diya"
                },
                "type": "text"
              }
            ],
            "contacts": [
              {
                "profile": {
                  "name": "Shop Owner"
                },
                "wa_id": "919876543210"
              }
            ]
          }
        }
      ]
    }
  ]
}
```

### Response

```json
{
  "status": "ok",
  "entry_name": "UD-2026-00008",
  "customer": "Ramesh Kumar",
  "balance_after": 3400.0
}
```

### NLU Parsing Patterns

The webhook parses these Hinglish patterns:

| Pattern | Example | Result |
|---|---|---|
| `{name} ko {amount} udhaar diya` | `Ramesh ko 200 udhaar diya` | Credit Given → ₹200 |
| `{name} ko {amount}` | `Mohan ko 50` | Credit Given → ₹50 |
| `{name} ne {amount} diye` | `Suresh ne 500 diye` | Payment Received → ₹500 |
| `{amount} mil gaye {name} se` | `300 mil gaye Ramesh se` | Payment Received → ₹300 |
| `{amount} aaye {name} se` | `200 aaye Suresh se` | Payment Received → ₹200 |

### Error Responses

```json
// Unparsable message
{"status": "unparsed", "text": "kuch samajh nahi aaya"}

// Invalid signature
{"message": "Invalid webhook signature", "exc_type": "PermissionError"}

// Missing signature (when app_secret is configured)
{"message": "Missing webhook signature", "exc_type": "PermissionError"}
```

## Credit Limit Check

Internal function triggered by `doc_events` — no API endpoint.

| Trigger | Condition | Action |
|---|---|---|
| `Udhaar Entry.on_update` | Customer's `current_balance > credit_limit` and `credit_limit > 0` | Creates a `Notification Log` entry with type "Alert" |

## Fixtures

Demo data loaded during `install-app` via patch `kirana_ledger.patches.add_demo_data`:

- **7 Udhaar Customers**: Ramesh, Suresh, Mohan, Lakshmi, Venkatesh, Fathima, Krishna
- **7 Udhaar Entries**: mix of credit given and payment received
- **5 Quick Inventory Items**: rice, oil, salt, detergent, biscuits

## Site Config

| Key | Type | Purpose |
|---|---|---|
| `whatsapp_app_secret` | string | Meta App Secret for webhook signature verification |
| `developer_mode` | 0/1 | Enable DocType customization in UI |
