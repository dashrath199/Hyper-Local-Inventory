<div align="center">

# 📒 Kirana Ledger

**Hyper-Local Inventory + Udhaar (Credit) Ledger for Kirana Shops**  
*An ERPNext v15 Custom App — Portfolio / Demo*

[![ERPNext v15](https://img.shields.io/badge/ERPNext-v15-%2328a745?style=flat-square&logo=erpnext)](https://erpnext.com)
[![CI](https://img.shields.io/github/actions/workflow/status/dashrath199/Hyper-Local-Inventory/ci.yml?style=flat-square&label=CI&logo=githubactions)](https://github.com/dashrath199/Hyper-Local-Inventory/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](#license)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)]()

</div>

---

## 📸 Demo Screenshots

> *These are placeholder descriptions. Once installed on a Frappe Bench, capture actual screenshots and add them here.*

<details>
<summary><b>🖥️ Click to view screenshot mockups</b></summary>

### Udhaar Ledger Workspace

```
┌─────────────────────────────────────────────────────┐
│  📒 Kirana Ledger                                   │
│                                                     │
│  ┌──────────────────┐  ┌──────────────────┐        │
│  │ Total Outstanding │  │ Customers Over    │        │
│  │     ₹20,100       │  │     Limit: 3      │        │
│  └──────────────────┘  └──────────────────┘        │
│                                                     │
│  [New Udhaar Entry]  [All Customers]                │
│  [Daily Summary]     [Over Limit Report]             │
└─────────────────────────────────────────────────────┘
```

*Replace this ASCII mockup with an actual screenshot of the Udhaar Ledger workspace.*

### Udhaar Entry Form

```
┌─────────────────────────────────────────────────────┐
│  Udhaar Entry  ●  UD-2026-00001                     │
│                                                     │
│  Customer:   [Ramesh Kumar            ▼]            │
│  Type:       [Credit Given            ▼]            │
│  Amount:     [₹    200                            ] │
│  Items:      [चीनी, चाय पत्ती, दूध                ] │
│  Date:       [07/09/2026                           ] │
│                                                     │
│  ┌──────────┐  ┌──────────┐                         │
│  │   Save   │  │  Submit  │                         │
│  └──────────┘  └──────────┘                         │
└─────────────────────────────────────────────────────┘
```

### Daily Udhaar Summary Report

| Date | Entry Type | Transactions | Total Amount |
|---|---|---|---|
| 2026-07-09 | Credit Given | 15 | ₹8,500 |
| 2026-07-09 | Payment Received | 8 | ₹3,200 |
| 2026-07-08 | Credit Given | 12 | ₹6,100 |

*(Actual report output from Frappe's Query Report viewer.)*

### WhatsApp Webhook Demo (API)

```
POST /api/method/kirana_ledger.api.whatsapp_webhook
Content-Type: application/json

→ "Ramesh ko 200 udhaar diya"
← ✅ Recorded ₹200 credit given to Ramesh Kumar.
   Total outstanding: ₹3,200
```

</details>

---

## ✨ Features

| Feature | Description |
|---|---|
| **📒 Udhaar Customer Tracking** | Maintain running balances for each customer with multi-language support (Hindi, Tamil, Telugu, Malayalam, Kannada, English) |
| **💸 Udhaar (Credit) Entries** | Record credit given or payment received. Submittable DocType with automatic balance computation via `before_save` hook |
| **📦 Quick Inventory** | Approximate stock tracking — no forced Stock Ledger accounting. Simple item name, estimate, and reorder flag |
| **📊 3 Query Reports** | Daily Udhaar Summary, Customers Over Credit Limit, Top Overdue Customers |
| **📋 Dedicated Workspace** | Number Cards for Total Outstanding and Customers Over Limit. Shortcuts to New Entry, Customers, Reports |
| **🔔 Credit Limit Alerts** | System Notification triggers automatically when a customer exceeds their credit limit |
| **📱 WhatsApp API Integration** | Webhook endpoint that parses Hinglish messages like "Ramesh ko 200 udhaar diya" into structured Udhaar Entries |
| **🎭 Demo Data** | 7 sample customers, 7 transactions, 5 inventory items — installed automatically with the app |

---

## 🚀 Quick Install

```bash
# 1. Get the app
bench get-app https://github.com/YOUR_USERNAME/kirana_ledger

# 2. Create a site (if needed)
bench new-site kirana-demo.local --admin-password admin

# 3. Install the app
bench --site kirana-demo.local install-app kirana_ledger

# 4. Set developer mode to explore DocTypes in UI
bench --site kirana-demo.local set-config developer_mode 1

# 5. Build and restart
bench build
bench restart
```

> **That's it.** Demo data is loaded automatically during installation. Log in to `http://kirana-demo.local:8000` and explore the **Udhaar Ledger** workspace.

---

## 🧱 What's Inside

### DocTypes

| DocType | Key Fields | Behavior |
|---|---|---|
| **Udhaar Customer** | `customer_name`, `phone`, `preferred_language` (6 options), `credit_limit`, `current_balance` (read-only), `last_payment_date` | Balance auto-maintained by linked Udhaar Entries. Warns on credit limit breach at save. |
| **Udhaar Entry** | `customer` (Link), `entry_type` (Credit Given / Payment Received), `amount`, `balance_after` (read-only), `items_description` (Small Text - no SKU forced) | `before_save` computes running balance. `on_submit`/`on_cancel` updates customer. Submittable. |
| **Quick Inventory Item** | `item_name`, `current_stock_estimate` (Float), `reorder_flag` (Check) | Deliberately thin. Approximates real stock rather than forcing exact ledger accounting. |

### Reports (Query Reports)

| Report | SQL Logic | Use Case |
|---|---|---|
| **Daily Udhaar Summary** | Groups by `date` and `entry_type` with date range filter | "How much udhaar did I give today vs. collected?" |
| **Customers Over Credit Limit** | `WHERE credit_limit > 0 AND current_balance > credit_limit` | "Who do I need to call for payment?" Shows language column for WhatsApp follow-up |
| **Top Overdue Customers** | `WHERE current_balance > 0 ORDER BY current_balance DESC` | "Who owes me the most money?" |

### Workspace: Udhaar Ledger

Two Number Cards + four shortcuts in a clean card-based layout:

- **Number Card**: Total Outstanding Udhaar (Sum of `current_balance`)
- **Number Card**: Customers Over Limit (Count with filter)
- **Shortcuts**: New Udhaar Entry, All Customers, Daily Summary Report, Over Limit Report

### Notifications

| Event | Condition | Action |
|---|---|---|
| `Udhaar Customer` → `current_balance` changes | `doc.current_balance > doc.credit_limit and doc.credit_limit > 0` | System Notification to all users with **Shop Owner** role |

### API Endpoint

```http
POST /api/method/kirana_ledger.api.whatsapp_webhook
```

Parses Hinglish/Natural language messages into Udhaar Entries:

| Input Message | Parsed Result |
|---|---|
| "Ramesh ko 200 udhaar diya" | Credit Given → ₹200 for Ramesh |
| "Suresh ne 500 diye" | Payment Received → ₹500 from Suresh |
| "300 mil gaye Ramesh se" | Payment Received → ₹300 from Ramesh |

> **Security**: The webhook verifies `X-Hub-Signature-256` against the `whatsapp_app_secret` site config. Unauthenticated requests are rejected in production mode.

---

## 📁 Project Structure

```
kirana_ledger/
├── __init__.py
├── setup.py / setup.cfg / requirements.txt / MANIFEST.in
├── license.txt / .gitignore
├── README.md
└── kirana_ledger/
    ├── __init__.py              # App version & metadata
    ├── hooks.py                 # Frappe configuration
    ├── api.py                   # WhatsApp webhook + credit limit check
    ├── patches/
    │   ├── __init__.py
    │   └── add_demo_data.py     # Seeds 7 customers, 7 entries, 5 items
    ├── fixtures/
    │   └── demo_data.json       # Realistic sample data in Hindi/Tamil/Malayalam
    ├── doctype/
    │   ├── udhaar_customer/     # DocType JSON + Python controller
    │   ├── udhaar_entry/        # DocType JSON + Python controller (before_save/on_submit)
    │   └── quick_inventory_item/ # DocType JSON + Python controller
    ├── report/
    │   ├── daily_udhaar_summary/
    │   ├── customers_over_credit_limit/
    │   └── top_overdue_customers/
    ├── workspace/
    │   └── udhaar_ledger/       # Number Cards + Shortcuts
    └── notification/
        └── credit_limit_breach/ # Value Change → System Notification
```

---

## ⚠️ Architecture Rationale

**This app demonstrates fluent Frappe/ERPNext v15 development — DocTypes, Query Reports, Workspaces, Notifications, doc_events, Patches, Fixtures, and API design.**

It is **not** the right architecture for its intended users. Here's why:

| Concern | ERPNext Approach | What a Kirana Owner Actually Needs |
|---|---|---|
| **Primary UX** | Desktop-grade admin UI (Frappe Desk) | WhatsApp — no app to install |
| **Entry Speed** | 30–60s to log one udhaar | 5–10s (type "Ramesh ko 200" in WhatsApp) |
| **Infrastructure** | MariaDB + Redis + Python workers per site | Shared Postgres or lightweight API |
| **Offline** | Online-only | WhatsApp queues offline natively |
| **Language** | Partial UI translations | Regional language via WhatsApp's native rendering |
| **Inventory** | Full Stock Ledger with valuation | "Have about 12 bags" — approximations only |
| **Notifications** | Email / Slack / System | WhatsApp — the one channel that matters |

### The Real Architecture Would Be

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Shop Owner   │────▶│ WhatsApp Business │────▶│ FastAPI Backend │
│ (WhatsApp)   │     │  Cloud API (Meta) │     │ + Supabase/DB   │
└──────────────┘     └──────────────────┘     └─────────────────┘
```

**This ERPNext app shows I can build Frappe DocTypes, reports, and workspaces fluently. It does not claim this is the right stack for a real kirana product.** It's a portfolio piece demonstrating Frappe/ERPNext development skills with full transparency about architectural trade-offs.

---

## 🛠️ Development Notes

### Adding a New Field

```bash
# Edit the DocType JSON, then run:
bench --site yoursite.local migrate
```

### Adding a New Report

1. Create `report/<report_name>/<report_name>.json` with SQL query
2. The report is auto-discovered — no hooks.py registration needed

### Testing the WhatsApp Webhook

```bash
curl -X POST \
  https://yoursite.local/api/method/kirana_ledger.api.whatsapp_webhook \
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

### Setting the Webhook Secret

```bash
bench --site yoursite.local set-config whatsapp_app_secret "your_meta_app_secret"
```

---

## 📄 License

MIT © 2026 Kirana Tech

---

<div align="center">

**Built with [Frappe](https://frappeframework.com) & [ERPNext](https://erpnext.com)**  
*For portfolio/demo purposes. Not recommended for production kirana deployments.*

</div>
