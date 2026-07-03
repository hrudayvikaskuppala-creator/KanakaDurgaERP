"""
===========================================
 Reports Page
===========================================
Business reports built on top of the existing services: Sales,
Purchases, Stock (with low-stock highlighting) and Customers.
Each report can be exported to CSV.
"""

import csv
import os
from tkinter import ttk, filedialog, messagebox

import customtkinter as ctk

from assets.themes import colors
from services.sales_service import load_sales
from services.purchase_service import load_purchases
from services.product_service import get_all_products
from services.customer_service import get_all_customers
from services.pos_transaction_service import load_all_transactions
from ui.components.watermark import add_watermark


REPORTS = {
    "Sales": {
        "columns": (
            "Invoice", "Date", "Customer", "Product",
            "Qty", "Total", "Payment", "Warranty"
        ),
        "keys": (
            "invoice_no", "sale_date", "customer", "product",
            "quantity", "total", "payment_mode", "warranty_type"
        ),
        "loader": load_sales,
        "amount_key": "total",
    },
    "Purchases": {
        "columns": (
            "ID", "Invoice", "Date", "Supplier", "Product",
            "Qty", "Price", "GST", "Total", "Discount"
        ),
        "keys": None,   # rows already come as sqlite3.Row matching table order
        "loader": load_purchases,
        "amount_key": "total",
    },

    "Stock": {
        "columns": ("ID", "Brand", "Model", "Capacity", "Stock", "Selling Price"),
        "keys": ("id", "brand", "model", "capacity", "stock", "selling_price"),
        "loader": get_all_products,
        "amount_key": None,
    },
    "Customers": {
        "columns": ("ID", "Name", "Mobile", "Vehicle", "Outstanding", "Status"),
        "keys": ("id", "customer_name", "mobile", "vehicle_number", "outstanding", "status"),
        "loader": get_all_customers,
        "amount_key": "outstanding",
    },
    "POS Transactions": {
        "columns": (
            "Invoice", "Amount", "Payment Mode", "Provider",
            "Transaction ID", "Approval Code", "Reference No", "Status", "Date"
        ),
        "keys": (
            "invoice_no", "amount", "payment_mode", "provider",
            "transaction_id", "approval_code", "reference_no", "status", "created_date"
        ),
        "loader": load_all_transactions,
        "amount_key": "amount",
    },
}


class ReportsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        add_watermark(self)

        self.current_report = "Sales"
        self.current_rows = []

        title = ctk.CTkLabel(
            self,
            text="Reports",
            font=colors.FONT_H1
        )
        title.pack(anchor="w", padx=10, pady=(10, 0))

        subtitle = ctk.CTkLabel(
            self,
            text="View and export your business reports.",
            font=colors.FONT_BODY,
            text_color=colors.TEXT_LIGHT
        )
        subtitle.pack(anchor="w", padx=10, pady=(0, 15))

        # ------------------ Tabs ------------------
        tab_bar = ctk.CTkFrame(self, fg_color="transparent")
        tab_bar.pack(fill="x", padx=10)

        self.tab_buttons = {}

        for name in REPORTS.keys():
            btn = ctk.CTkButton(
                tab_bar,
                text=name,
                width=140,
                height=colors.BUTTON_HEIGHT,
                corner_radius=colors.RADIUS_SM,
                font=colors.FONT_BUTTON,
                fg_color=colors.SIDEBAR_BUTTON if name != self.current_report else colors.PRIMARY,
                hover_color=colors.PRIMARY_HOVER,
                command=lambda n=name: self.switch_report(n)
            )
            btn.pack(side="left", padx=(0, 8), pady=5)
            self.tab_buttons[name] = btn

        ctk.CTkButton(
            tab_bar,
            text="⬇ Export CSV",
            width=140,
            height=colors.BUTTON_HEIGHT,
            corner_radius=colors.RADIUS_SM,
            font=colors.FONT_BUTTON,
            fg_color=colors.SUCCESS,
            hover_color=colors.SUCCESS_HOVER,
            command=self.export_csv
        ).pack(side="right", padx=5, pady=5)

        # ------------------ Summary Card ------------------
        self.summary_frame = ctk.CTkFrame(
            self, fg_color=colors.CARD, corner_radius=colors.RADIUS
        )
        self.summary_frame.pack(fill="x", padx=10, pady=10)

        self.summary_count = ctk.CTkLabel(
            self.summary_frame, text="Records: 0",
            font=colors.FONT_BODY_BOLD
        )
        self.summary_count.pack(side="left", padx=20, pady=12)

        self.summary_amount = ctk.CTkLabel(
            self.summary_frame, text="",
            font=colors.FONT_BODY_BOLD, text_color=colors.SUCCESS
        )
        self.summary_amount.pack(side="left", padx=20, pady=12)

        # ------------------ Table ------------------
        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(table_frame, show="headings", height=18)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("low_stock", background="#FEE2E2")

        self.switch_report("Sales")

    # ------------------------------------------------------------
    def switch_report(self, name):

        self.current_report = name

        for report_name, btn in self.tab_buttons.items():
            btn.configure(
                fg_color=colors.PRIMARY if report_name == name
                else colors.SIDEBAR_BUTTON
            )

        self.load_report()

    def load_report(self):

        config = REPORTS[self.current_report]

        columns = config["columns"]
        self.tree.configure(columns=columns)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = config["loader"]()
        self.current_rows = rows

        total_amount = 0
        low_stock_count = 0

        for row in rows:
            if config["keys"]:
                values = [row[key] for key in config["keys"]]
            else:
                values = list(row)

            tags = ()

            if self.current_report == "Stock":
                try:
                    if row["stock"] <= row["min_stock"]:
                        tags = ("low_stock",)
                        low_stock_count += 1
                except Exception:
                    pass

            self.tree.insert("", "end", values=values, tags=tags)

            if config["amount_key"]:
                try:
                    total_amount += float(row[config["amount_key"]] or 0)
                except Exception:
                    pass

        self.summary_count.configure(text=f"Records: {len(rows)}")

        if config["amount_key"] and self.current_report != "Customers":
            self.summary_amount.configure(
                text=f"Total {config['amount_key'].replace('_', ' ').title()}: ₹ {total_amount:,.2f}"
            )
        elif self.current_report == "Customers":
            self.summary_amount.configure(
                text=f"Total Outstanding: ₹ {total_amount:,.2f}"
            )
        elif self.current_report == "Stock":
            self.summary_amount.configure(
                text=f"Low Stock Items: {low_stock_count}"
            )
        else:
            self.summary_amount.configure(text="")

    # ------------------------------------------------------------
    def export_csv(self):

        if not self.current_rows:
            messagebox.showinfo("Export", "No data to export.")
            return

        default_name = f"{self.current_report.lower()}_report.csv"

        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV Files", "*.csv")]
        )

        if not path:
            return

        columns = REPORTS[self.current_report]["columns"]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)

            for item_id in self.tree.get_children():
                writer.writerow(self.tree.item(item_id)["values"])

        messagebox.showinfo(
            "Export Complete",
            f"Report exported to:\n{os.path.abspath(path)}"
        )
