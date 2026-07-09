# Kirana Ledger — Setup Guide

Complete walkthrough for installing and running the Kirana Ledger ERPNext v15 custom app.

## Prerequisites

- Frappe Bench v15+ ([install guide](https://github.com/frappe/bench))
- Python 3.11+
- Node.js 18+
- MariaDB 10.6+ & Redis

## Step-by-Step Installation

### 1. Create a Frappe Bench

```bash
# If you don't have a bench yet:
bench init frappe-bench --frappe-branch version-15
cd frappe-bench
```

### 2. Get the App

```bash
bench get-app https://github.com/YOUR_USERNAME/kirana_ledger
```

### 3. Create a Site

```bash
bench new-site kirana-demo.local --admin-password admin
```

### 4. Install the App

```bash
bench --site kirana-demo.local install-app kirana_ledger
```

The app will:
- Create all 3 DocTypes (Udhaar Customer, Udhaar Entry, Quick Inventory Item)
- Register 3 Query Reports
- Set up the Udhaar Ledger workspace with 2 Number Cards and 4 Shortcuts
- Configure the Credit Limit Breach notification
- Seed demo data: 7 customers, 7 transactions, 5 inventory items
- Create the "Shop Owner" role

### 5. Set Developer Mode (Recommended)

```bash
bench --site kirana-demo.local set-config developer_mode 1
```

This exposes DocType field customization in the UI.

### 6. Build Assets & Restart

```bash
bench build
bench restart
```

## Post-Installation

### Login

1. Open `http://kirana-demo.local:8000` in your browser
2. Login with: **Administrator** / **admin** (the password you set with `--admin-password`)
3. You'll see the **Udhaar Ledger** workspace in the Module list

### Explore

1. **Udhaar Ledger Workspace** — Check the Total Outstanding Number Card and Customers Over Limit
2. **Udhaar Customer** — View the 7 pre-loaded customers (Ramesh, Suresh, Mohan, Lakshmi, Venkatesh, Fathima, Krishna)
3. **Udhaar Entry** — Create a new entry: Credit Given to Ramesh for ₹300
4. **Quick Inventory Item** — Check the 5 items; note that "Tata Salt" and "Parle-G" need reorder
5. **Reports** — Run "Daily Udhaar Summary" with a date range, see "Customers Over Credit Limit" (Venkatesh and Krishna are over their limits)

### Testing the WhatsApp Webhook

```bash
curl -X POST \
  http://kirana-demo.local:8000/api/method/kirana_ledger.api.whatsapp_webhook \
  -H "Content-Type: application/json" \
  -d '{
    "entry": [{
      "changes": [{
        "value": {
          "messages": [{
            "from": "919876543210",
            "text": {"body": "Ramesh ko 200 udhaar diya"}
          }]
        }
      }]
    }]
  }'
```

Expected response:
```json
{
  "status": "ok",
  "entry_name": "UD-2026-00008",
  "customer": "Ramesh Kumar",
  "balance_after": 3400.0
}
```

### Setting the Webhook Secret (Optional)

For production-like testing with signature verification:

```bash
bench --site kirana-demo.local set-config whatsapp_app_secret "your_meta_app_secret"
```

## Taking Screenshots for Portfolio

Use these exact views to capture professional screenshots:

| View | What to Capture | Tip |
|---|---|---|
| **Udhaar Ledger Workspace** | Full workspace with Number Cards + Shortcuts | Use browser at 1280x900 |
| **Udhaar Entry Form** | The New Entry form with a customer selected | Show the before_save balance computation |
| **Customers Over Limit Report** | Query Report output showing Venkatesh & Krishna | Set descending by Excess column |
| **Daily Udhaar Summary** | Grouped by date with Credit Given / Payment Received | Ensure at least 2 days of data |
| **Udhaar Customer List** | All 7 customers with balances and languages | Sort by Balance descending |
| **Notification Log** | Credit Limit Breach system notification | Test by creating an entry that pushes a customer over limit |

## Troubleshooting

### "DocType not found" on install

```bash
bench --site kirana-demo.local migrate
```

### Reports not showing

Reports are auto-discovered. If missing, run:
```bash
bench clear-cache
bench --site kirana-demo.local migrate
```

### Wrong language in demo data

Edit `kirana_ledger/fixtures/demo_data.json`, then re-run the patch:
```bash
bench --site kirana-demo.local migrate
```
