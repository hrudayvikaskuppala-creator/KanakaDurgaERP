# BatteryERP Professional

A desktop ERP application (built with Python + customtkinter) for managing a
battery shop's customers, products, suppliers, purchases, sales, reports and
users.

## Features

- 🔐 Secure login with bcrypt-hashed passwords and role-based access (Admin / Manager / Cashier)
- 👤 Full user management — Admin can create, edit, delete users, reset passwords and assign roles
- 👥 Customer management with outstanding balance tracking
- 📦 Product / inventory management with low-stock alerts
- 🚚 Supplier management
- 🛒 Smart Purchase workflow — selecting a supplier narrows the product list to their purchase history and auto-fills the last price paid
- 🧾 Sales invoicing with printable / exportable receipts
- 📊 Reports (Sales, Purchases, Stock, Customers) with CSV export
- ⚙️ Settings — company profile (used on invoices), appearance & currency, change password
- 🎬 Branded loading screen after login (supports a custom image + audio — see `Source/assets/splash/README.md`)
- 📝 Basic audit log of logins/logouts and user-management actions

## Getting Started

```bash
cd Source
pip install -r ../requirements.txt
python main.py
```

Default login: `admin` / `admin123` (change this after first login from
Settings → Change Password).

## Project Structure

```
Source/
├── main.py                 Entry point
├── config.py                App name / version
├── database/                SQLite connection + migrations
├── models/                   Table-level DB access
├── services/                 Business logic
├── ui/                        customtkinter screens
│   └── components/            Reusable form/table widgets
└── assets/
    ├── themes/colors.py       Central color & font palette
    └── splash/                Optional loading-screen image/audio
```
