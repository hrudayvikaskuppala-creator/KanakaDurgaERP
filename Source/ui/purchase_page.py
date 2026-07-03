"""
===========================================
 Purchase Page (single-screen purchase entry)
===========================================
Lets the user record a complete supplier invoice - possibly with
several different products - from one screen:

  1. Pick (or quick-add) a Supplier.
  2. Pick (or quick-add) a Product, set Qty / Price / GST / Discount,
     and add it to the invoice's item list ("cart").
  3. Repeat for as many products as the invoice has.
  4. Set payment info (Paid / Unpaid / Partial + amount paid).
  5. Save - every item is written as a purchase line under the same
     invoice number, stock is increased for each product, and any
     unpaid balance is added to the supplier's outstanding total.

No navigating to the Supplier or Product page is required for a
normal purchase entry.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime

from assets.themes import colors

from services.product_service import (
    increase_stock,
    get_product_names,
    get_product_details
)

from services.supplier_service import (
    get_supplier_names,
    adjust_outstanding,
    add_supplier,
    find_duplicate_supplier
)

from services.purchase_service import (
    add_purchase,
    load_purchases,
    remove_purchase,
    find_purchase,
    get_products_for_supplier,
    get_last_purchase,
    invoice_number_exists
)

from ui.components.quick_add_modal import (
    open_quick_add_supplier,
    open_quick_add_product
)
from ui.components.import_review_modal import pick_invoice_and_review
from ui.components.validators import (
    attach_digits_only,
    attach_decimal_only,
    attach_alnum,
    validate_positive_number,
    validate_gst,
    run_checks,
    show_validation_error
)
from ui.components.watermark import add_watermark

HISTORY_COLUMNS = ("ID", "Invoice", "Date", "Supplier", "Product", "Qty", "Price", "GST", "Total", "Discount")
PAYMENT_STATUSES = ["Paid", "Unpaid", "Partial"]


class PurchasePage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        add_watermark(self)

        self.selected_purchase = None
        self.showing_all_products = True
        self.cart = []  # list of dicts: product, qty, price, gst, discount, total

        self.create_widgets()
        self.load_purchases()

    # ==================================================================
    # UI
    # ==================================================================
    def create_widgets(self):

        title = ctk.CTkLabel(
            self, text="🛒 Purchase Management", font=colors.FONT_H1, text_color=colors.PRIMARY
        )
        title.pack(pady=(10, 4))

        subtitle = ctk.CTkLabel(
            self,
            text="Add a supplier, add one or more products, then save the whole invoice in one go.",
            font=colors.FONT_BODY, text_color=colors.TEXT_LIGHT
        )
        subtitle.pack(pady=(0, 12))

        # ============================================================
        # Card 1 - Invoice + Supplier + Payment
        # ============================================================
        info_card = ctk.CTkFrame(self, fg_color=colors.CARD, corner_radius=colors.RADIUS)
        info_card.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(
            info_card, text="Invoice & Supplier", font=colors.FONT_H3, text_color=colors.PRIMARY
        ).grid(row=0, column=0, columnspan=6, sticky="w", padx=18, pady=(14, 8))

        ctk.CTkLabel(info_card, text="Invoice No", font=colors.FONT_BODY_BOLD).grid(
            row=1, column=0, padx=18, pady=8, sticky="w"
        )
        self.invoice_entry = ctk.CTkEntry(info_card, width=180)
        self.invoice_entry.grid(row=1, column=1, padx=8, pady=8, sticky="w")
        attach_alnum(self.invoice_entry)

        ctk.CTkLabel(info_card, text="Date", font=colors.FONT_BODY_BOLD).grid(
            row=1, column=2, padx=8, pady=8, sticky="w"
        )
        self.date_entry = ctk.CTkEntry(info_card, width=140)
        self.date_entry.grid(row=1, column=3, padx=8, pady=8, sticky="w")
        self.date_entry.insert(0, datetime.today().strftime("%d-%m-%Y"))

        ctk.CTkLabel(info_card, text="Payment Status", font=colors.FONT_BODY_BOLD).grid(
            row=1, column=4, padx=8, pady=8, sticky="w"
        )
        self.payment_status = ctk.CTkComboBox(
            info_card, width=140, values=PAYMENT_STATUSES, command=self.on_payment_status_changed
        )
        self.payment_status.set("Paid")
        self.payment_status.grid(row=1, column=5, padx=(8, 18), pady=8, sticky="w")

        ctk.CTkLabel(info_card, text="Supplier", font=colors.FONT_BODY_BOLD).grid(
            row=2, column=0, padx=18, pady=(8, 8), sticky="w"
        )
        self.supplier_entry = ctk.CTkComboBox(
            info_card, width=280, values=get_supplier_names(), command=self.on_supplier_selected
        )
        self.supplier_entry.grid(row=2, column=1, columnspan=2, padx=8, pady=(8, 8), sticky="w")
        self.supplier_entry.set("")  # avoid CTk showing its own class name when values is empty

        ctk.CTkButton(
            info_card, text="➕ New Supplier", width=140, height=28,
            font=colors.FONT_SMALL_BOLD, fg_color=colors.SECONDARY, hover_color=colors.SECONDARY_HOVER,
            command=self.quick_add_supplier
        ).grid(row=2, column=3, padx=8, pady=(8, 8), sticky="w")

        ctk.CTkLabel(info_card, text="Amount Paid", font=colors.FONT_BODY_BOLD).grid(
            row=2, column=4, padx=8, pady=(8, 8), sticky="w"
        )
        self.amount_paid_entry = ctk.CTkEntry(info_card, width=140, state="disabled")
        self.amount_paid_entry.grid(row=2, column=5, padx=(8, 18), pady=(8, 8), sticky="w")
        attach_decimal_only(self.amount_paid_entry)

        # ============================================================
        # Card 2 - Add Item
        # ============================================================
        item_card = ctk.CTkFrame(self, fg_color=colors.CARD, corner_radius=colors.RADIUS)
        item_card.pack(fill="x", padx=20, pady=6)

        header_row = ctk.CTkFrame(item_card, fg_color="transparent")
        header_row.grid(row=0, column=0, columnspan=6, sticky="ew", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            header_row, text="Add Product to Invoice", font=colors.FONT_H3, text_color=colors.PRIMARY
        ).pack(side="left")

        self.product_scope_label = ctk.CTkLabel(
            header_row, text="", font=colors.FONT_SMALL, text_color=colors.TEXT_LIGHT
        )
        self.product_scope_label.pack(side="left", padx=15)

        ctk.CTkButton(
            header_row, text="Show All Products", width=140, height=26,
            font=colors.FONT_SMALL_BOLD, fg_color=colors.SIDEBAR_BUTTON,
            command=self.show_all_products
        ).pack(side="right")

        ctk.CTkLabel(item_card, text="Product", font=colors.FONT_BODY_BOLD).grid(
            row=1, column=0, padx=18, pady=8, sticky="w"
        )
        self.product_entry = ctk.CTkComboBox(
            item_card, width=300, values=get_product_names(), command=self.on_product_selected
        )
        self.product_entry.grid(row=1, column=1, columnspan=2, padx=8, pady=8, sticky="w")
        self.product_entry.set("")  # avoid CTk showing its own class name when values is empty

        ctk.CTkButton(
            item_card, text="➕ New Product", width=140, height=28,
            font=colors.FONT_SMALL_BOLD, fg_color=colors.SECONDARY, hover_color=colors.SECONDARY_HOVER,
            command=self.quick_add_product
        ).grid(row=1, column=3, padx=8, pady=8, sticky="w")

        self.stock_preview = ctk.CTkLabel(
            item_card, text="", font=colors.FONT_SMALL_BOLD, text_color=colors.INFO
        )
        self.stock_preview.grid(row=2, column=1, columnspan=3, padx=8, sticky="w")

        # ---- Quantity ----
        ctk.CTkLabel(item_card, text="Quantity", font=colors.FONT_BODY_BOLD).grid(
            row=3, column=0, padx=18, pady=(14, 8), sticky="w"
        )
        qty_frame = ctk.CTkFrame(item_card, fg_color="transparent")
        qty_frame.grid(row=3, column=1, padx=8, pady=(14, 8), sticky="w")

        ctk.CTkButton(
            qty_frame, text="−", width=32, height=32,
            fg_color=colors.SIDEBAR_BUTTON, command=self.decrease_qty
        ).pack(side="left")

        self.quantity_entry = ctk.CTkEntry(qty_frame, width=70, justify="center")
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.pack(side="left", padx=6)
        attach_digits_only(self.quantity_entry)

        ctk.CTkButton(
            qty_frame, text="+", width=32, height=32,
            fg_color=colors.SIDEBAR_BUTTON, command=self.increase_qty
        ).pack(side="left")

        # ---- Price ----
        ctk.CTkLabel(item_card, text="Purchase Price", font=colors.FONT_BODY_BOLD).grid(
            row=3, column=2, padx=8, pady=(14, 8), sticky="w"
        )
        self.price_entry = ctk.CTkEntry(item_card, width=120)
        self.price_entry.grid(row=3, column=3, padx=8, pady=(14, 8), sticky="w")
        attach_decimal_only(self.price_entry)

        # ---- GST ----
        ctk.CTkLabel(item_card, text="GST %", font=colors.FONT_BODY_BOLD).grid(
            row=4, column=0, padx=18, pady=(8, 16), sticky="w"
        )
        self.gst_entry = ctk.CTkEntry(item_card, width=100)
        self.gst_entry.grid(row=4, column=1, padx=8, pady=(8, 16), sticky="w")
        attach_decimal_only(self.gst_entry)

        # ---- Discount ----
        ctk.CTkLabel(item_card, text="Discount %", font=colors.FONT_BODY_BOLD).grid(
            row=4, column=2, padx=8, pady=(8, 16), sticky="w"
        )
        self.discount_entry = ctk.CTkEntry(item_card, width=100)
        self.discount_entry.insert(0, "0")
        self.discount_entry.grid(row=4, column=3, padx=8, pady=(8, 16), sticky="w")
        attach_decimal_only(self.discount_entry)

        ctk.CTkButton(
            item_card, text="➕ Add Item to Invoice", height=colors.BUTTON_HEIGHT,
            font=colors.FONT_BUTTON, fg_color=colors.PRIMARY, hover_color=colors.PRIMARY_HOVER,
            corner_radius=colors.RADIUS_SM, command=self.add_item_to_cart
        ).grid(row=4, column=4, columnspan=2, padx=18, pady=(8, 16), sticky="w")

        # ============================================================
        # Card 3 - Invoice Items (cart) + Summary
        # ============================================================
        cart_card = ctk.CTkFrame(self, fg_color=colors.CARD, corner_radius=colors.RADIUS)
        cart_card.pack(fill="x", padx=20, pady=6)

        ctk.CTkLabel(
            cart_card, text="Invoice Items", font=colors.FONT_H3, text_color=colors.PRIMARY
        ).pack(anchor="w", padx=18, pady=(14, 4))

        cart_columns = ("Product", "Qty", "Price", "GST %", "Discount %", "Line Total")
        self.cart_tree = ttk.Treeview(cart_card, columns=cart_columns, show="headings", height=5)
        for col in cart_columns:
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=120, anchor="center")
        self.cart_tree.pack(fill="x", padx=18, pady=(0, 8))

        ctk.CTkButton(
            cart_card, text="🗑 Remove Selected Item", width=180, height=28,
            font=colors.FONT_SMALL_BOLD, fg_color=colors.DANGER, hover_color=colors.DANGER_HOVER,
            command=self.remove_cart_item
        ).pack(anchor="w", padx=18, pady=(0, 12))

        summary_inner = ctk.CTkFrame(cart_card, fg_color=colors.PRIMARY, corner_radius=colors.RADIUS)
        summary_inner.pack(fill="x", padx=18, pady=(0, 16))

        grid = ctk.CTkFrame(summary_inner, fg_color="transparent")
        grid.pack(fill="x", padx=18, pady=12)
        grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        def summary_label(col, caption):
            ctk.CTkLabel(grid, text=caption, font=colors.FONT_SMALL, text_color="#DBEAFE").grid(
                row=0, column=col, sticky="w"
            )
            value = ctk.CTkLabel(
                grid, text="₹ 0.00", font=(colors.FONT_FAMILY, 16, "bold"), text_color=colors.TEXT_ON_PRIMARY
            )
            value.grid(row=1, column=col, sticky="w", pady=(2, 0))
            return value

        self.subtotal_label = summary_label(0, "Subtotal")
        self.discount_label = summary_label(1, "Discount")
        self.gst_label = summary_label(2, "GST")
        self.grand_total_label = summary_label(3, "Grand Total")

        # ---------------- Buttons ----------------
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(
            button_frame, text="💾 Save Purchase Invoice", width=210, height=colors.BUTTON_HEIGHT,
            font=colors.FONT_BUTTON, fg_color=colors.SUCCESS, hover_color=colors.SUCCESS_HOVER,
            corner_radius=colors.RADIUS_SM, command=self.save_purchase
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            button_frame, text="✖ Clear", width=130, height=colors.BUTTON_HEIGHT,
            font=colors.FONT_BUTTON, fg_color=colors.SIDEBAR_BUTTON,
            corner_radius=colors.RADIUS_SM, command=self.clear_form
        ).grid(row=0, column=1, padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="📄 Import Invoice",
            width=180,
            height=colors.BUTTON_HEIGHT,
            font=colors.FONT_BUTTON,
            fg_color=colors.PRIMARY,
            hover_color=colors.PRIMARY_HOVER,
            corner_radius=colors.RADIUS_SM,
            command=self.import_invoice
        ).grid(row=0, column=2, padx=5)

        # ---------------- Search + History ----------------
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20)

        self.search_entry = ctk.CTkEntry(
            search_frame, width=300, placeholder_text="Search by invoice, supplier or product"
        )
        self.search_entry.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(
            search_frame, text="🔍 Search", fg_color=colors.PRIMARY,
            hover_color=colors.PRIMARY_HOVER, font=colors.FONT_BUTTON, command=self.search_purchase
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame, text="Show All", fg_color=colors.SIDEBAR_BUTTON,
            font=colors.FONT_BUTTON, command=self.load_purchases
        ).pack(side="left", padx=5)

        table_frame = ctk.CTkFrame(self, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(table_frame, columns=HISTORY_COLUMNS, show="headings", height=8)
        for col in HISTORY_COLUMNS:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.select_purchase)
        self.quantity_entry.bind("<KeyRelease>", lambda e: self.update_stock_preview())

        self.on_payment_status_changed()

    # ==================================================================
    # Quick-add integrations
    # ==================================================================
    def quick_add_supplier(self):
        def on_saved(name):
            self.supplier_entry.configure(values=get_supplier_names())
            self.supplier_entry.set(name)
            self.on_supplier_selected(name)

        open_quick_add_supplier(self, on_saved)

    def quick_add_product(self):
        def on_saved(name):
            self.product_entry.configure(values=get_product_names())
            self.product_entry.set(name)
            self.on_product_selected(name)

        open_quick_add_product(self, on_saved)

    def import_invoice(self):
        """
        'Import Invoice' button: pick a supplier's PDF/scanned/Word
        invoice, review the auto-extracted supplier + line items, then
        drop the confirmed items straight into the current cart (same
        totals math as adding them one at a time via the form above).
        """
        def on_confirm(supplier_data, invoice_no, date, line_items):
            supplier_name = supplier_data.get("supplier_name", "").strip()

            if supplier_name:
                if supplier_name not in get_supplier_names():
                    dup_reason = find_duplicate_supplier(
                        supplier_name,
                        supplier_data.get("mobile", ""),
                        supplier_data.get("gst_number", "")
                    )
                    if not dup_reason:
                        try:
                            add_supplier(
                                supplier_name,
                                supplier_data.get("mobile", ""),
                                supplier_data.get("gst_number", ""),
                                supplier_data.get("address", ""),
                                ""
                            )
                        except Exception:
                            pass  # Fall back to just filling the name below.

                self.supplier_entry.configure(values=get_supplier_names())
                self.supplier_entry.set(supplier_name)
                self.on_supplier_selected(supplier_name)

            if invoice_no:
                self.invoice_entry.delete(0, "end")
                self.invoice_entry.insert(0, invoice_no)

            if date:
                self.date_entry.delete(0, "end")
                self.date_entry.insert(0, date)

            known_products = {name.lower(): name for name in get_product_names()}
            added, unmatched = 0, []

            for item in line_items:
                product_name = item["product"]
                matched_name = known_products.get(product_name.lower())

                if not matched_name:
                    unmatched.append(product_name)
                    continue

                if any(c["product"].strip().lower() == matched_name.lower() for c in self.cart):
                    continue  # Already in this invoice - skip rather than double-add.

                qty = item.get("qty") or 1
                price = item.get("price") or 0
                gst = item.get("gst") or 0

                line_subtotal = qty * price
                gst_amt = line_subtotal * gst / 100
                line_total = line_subtotal + gst_amt

                self.cart.append({
                    "product": matched_name, "qty": qty, "price": price,
                    "gst": gst, "discount": 0, "total": line_total
                })
                self.cart_tree.insert("", "end", values=(
                    matched_name, int(qty), f"{price:.2f}", f"{gst:.2f}", "0.00", f"{line_total:.2f}"
                ))
                added += 1

            if added:
                self.refresh_summary()

            summary = f"Added {added} item(s) to this invoice."
            if unmatched:
                summary += (
                    "\n\nThese items weren't recognised as existing products, so "
                    "they were skipped - add them first (➕ New Product) or type "
                    "them manually, then re-import if needed:\n• " + "\n• ".join(unmatched)
                )
            messagebox.showinfo("Invoice Imported", summary)

        pick_invoice_and_review(self, on_confirm)

    # ==================================================================
    # Payment
    # ==================================================================
    def on_payment_status_changed(self, value=None):
        status = self.payment_status.get()

        if status == "Partial":
            self.amount_paid_entry.configure(state="normal")
        else:
            self.amount_paid_entry.configure(state="normal")
            self.amount_paid_entry.delete(0, "end")
            if status == "Paid":
                grand_total = self._cart_totals()[3]
                self.amount_paid_entry.insert(0, f"{grand_total:.2f}")
            else:
                self.amount_paid_entry.insert(0, "0")
            self.amount_paid_entry.configure(state="disabled")

    # ==================================================================
    # Supplier <-> Product smart integration
    # ==================================================================
    def on_supplier_selected(self, supplier_name=None):
        supplier_name = (supplier_name or self.supplier_entry.get()).strip()
        if not supplier_name:
            return

        history = get_products_for_supplier(supplier_name)

        if history:
            self.product_entry.configure(values=history)
            self.showing_all_products = False
            self.product_scope_label.configure(
                text=f"Showing {len(history)} product(s) previously bought from {supplier_name}"
            )
        else:
            self.product_entry.configure(values=get_product_names())
            self.showing_all_products = True
            self.product_scope_label.configure(
                text="No purchase history yet for this supplier — showing all products"
            )

        self.product_entry.set("")
        self.update_stock_preview()

    def show_all_products(self):
        self.product_entry.configure(values=get_product_names())
        self.showing_all_products = True
        self.product_scope_label.configure(text="")

    def on_product_selected(self, product_name=None):
        self.update_stock_preview()
        self.try_autofill_last_price()

    def try_autofill_last_price(self):
        supplier = self.supplier_entry.get().strip()
        product = self.product_entry.get().strip()
        if not supplier or not product:
            return

        last = get_last_purchase(supplier, product)
        if last:
            self.price_entry.delete(0, "end")
            self.price_entry.insert(0, str(last["purchase_price"]))
            self.gst_entry.delete(0, "end")
            self.gst_entry.insert(0, str(last["gst"]))

    def update_stock_preview(self):
        product = self.product_entry.get().strip()
        if not product:
            self.stock_preview.configure(text="")
            return

        data = get_product_details(product)
        if not data:
            self.stock_preview.configure(text="")
            return

        try:
            qty = int(self.quantity_entry.get() or 0)
        except ValueError:
            qty = 0

        current_stock = data["stock"]
        new_stock = current_stock + qty
        self.stock_preview.configure(
            text=f"📦 Current Stock: {current_stock}   →   New Stock After This Item: {new_stock}"
        )

    # ==================================================================
    # Quantity steppers
    # ==================================================================
    def increase_qty(self):
        try:
            qty = int(self.quantity_entry.get() or 0)
        except ValueError:
            qty = 0
        qty += 1
        self.quantity_entry.delete(0, "end")
        self.quantity_entry.insert(0, str(qty))
        self.update_stock_preview()

    def decrease_qty(self):
        try:
            qty = int(self.quantity_entry.get() or 0)
        except ValueError:
            qty = 0
        qty = max(1, qty - 1)
        self.quantity_entry.delete(0, "end")
        self.quantity_entry.insert(0, str(qty))
        self.update_stock_preview()

    # ==================================================================
    # Cart (multi-item invoice)
    # ==================================================================
    def add_item_to_cart(self):
        product = self.product_entry.get().strip()

        if not run_checks(
            (bool(product), "Please select or add a Product first."),
            validate_positive_number(self.quantity_entry.get(), "Quantity", allow_zero=False),
            validate_positive_number(self.price_entry.get(), "Purchase Price", allow_zero=False),
            validate_gst(self.gst_entry.get()),
            validate_positive_number(self.discount_entry.get() or "0", "Discount %"),
        ):
            return

        if any(item["product"].strip().lower() == product.lower() for item in self.cart):
            messagebox.showwarning(
                "Duplicate Item",
                f"'{product}' is already in this invoice's item list.\n\n"
                f"Remove it from the list below and re-add it if you need to "
                f"change the quantity, instead of adding it twice."
            )
            return

        qty = float(self.quantity_entry.get())
        price = float(self.price_entry.get())
        gst = float(self.gst_entry.get() or 0)
        discount = float(self.discount_entry.get() or 0)

        if discount > 100:
            show_validation_error("Discount % cannot be more than 100.")
            return

        line_subtotal = qty * price
        discount_amt = line_subtotal * discount / 100
        taxable = line_subtotal - discount_amt
        gst_amt = taxable * gst / 100
        line_total = taxable + gst_amt

        self.cart.append({
            "product": product, "qty": qty, "price": price,
            "gst": gst, "discount": discount, "total": line_total
        })

        self.cart_tree.insert("", "end", values=(
            product, int(qty), f"{price:.2f}", f"{gst:.2f}", f"{discount:.2f}", f"{line_total:.2f}"
        ))

        self.refresh_summary()

        # Reset just the item-entry fields so the next product can be added
        self.product_entry.set("")
        self.quantity_entry.delete(0, "end")
        self.quantity_entry.insert(0, "1")
        self.price_entry.delete(0, "end")
        self.gst_entry.delete(0, "end")
        self.discount_entry.delete(0, "end")
        self.discount_entry.insert(0, "0")
        self.stock_preview.configure(text="")

    def remove_cart_item(self):
        selected = self.cart_tree.focus()
        if not selected:
            messagebox.showwarning("Remove Item", "Select an item from the invoice list first.")
            return

        index = self.cart_tree.index(selected)
        self.cart_tree.delete(selected)
        del self.cart[index]
        self.refresh_summary()

    def _cart_totals(self):
        subtotal = sum(item["qty"] * item["price"] for item in self.cart)
        discount_amt = sum(item["qty"] * item["price"] * item["discount"] / 100 for item in self.cart)
        gst_amt = sum(
            (item["qty"] * item["price"] - item["qty"] * item["price"] * item["discount"] / 100)
            * item["gst"] / 100
            for item in self.cart
        )
        grand_total = subtotal - discount_amt + gst_amt
        return subtotal, discount_amt, gst_amt, grand_total

    def refresh_summary(self):
        subtotal, discount_amt, gst_amt, grand_total = self._cart_totals()
        self.subtotal_label.configure(text=f"₹ {subtotal:,.2f}")
        self.discount_label.configure(text=f"− ₹ {discount_amt:,.2f}")
        self.gst_label.configure(text=f"+ ₹ {gst_amt:,.2f}")
        self.grand_total_label.configure(text=f"₹ {grand_total:,.2f}")

        if self.payment_status.get() == "Paid":
            self.amount_paid_entry.configure(state="normal")
            self.amount_paid_entry.delete(0, "end")
            self.amount_paid_entry.insert(0, f"{grand_total:.2f}")
            self.amount_paid_entry.configure(state="disabled")

    # ==================================================================
    # Save / Delete / Search / History
    # ==================================================================
    def save_purchase(self):
        invoice = self.invoice_entry.get().strip()
        date = self.date_entry.get().strip()
        supplier = self.supplier_entry.get().strip()

        if not run_checks(
            (bool(invoice), "Invoice No is required."),
            (bool(supplier), "Please select or add a Supplier."),
            (bool(self.cart), "Add at least one product to the invoice before saving."),
        ):
            return

        if invoice_number_exists(invoice, supplier):
            messagebox.showwarning(
                "Duplicate Invoice",
                f"Invoice '{invoice}' has already been recorded for {supplier}.\n\n"
                f"If this is a new invoice, please use a different invoice number."
            )
            return

        subtotal, discount_amt, gst_amt, grand_total = self._cart_totals()

        try:
            paid_amount = float(self.amount_paid_entry.get() or 0)
        except ValueError:
            show_validation_error("Amount Paid must be a valid number.")
            return

        for item in self.cart:
            add_purchase(
                invoice, date, supplier, item["product"], item["qty"],
                item["price"], item["gst"], item["total"], item["discount"]
            )
            increase_stock(item["product"], item["qty"])

        balance_due = max(0.0, grand_total - paid_amount)
        if balance_due > 0:
            adjust_outstanding(supplier, balance_due)

        self.load_purchases()
        self.clear_form()

        messagebox.showinfo(
            "Success",
            f"Purchase invoice saved and stock updated for {len(self.cart) if self.cart else 0} item(s).\n"
            f"Grand Total: ₹ {grand_total:,.2f}" + (
                f"\nOutstanding added to supplier balance: ₹ {balance_due:,.2f}" if balance_due > 0 else ""
            )
        )

    def delete_purchase(self):
        if self.selected_purchase is None:
            messagebox.showwarning("Delete", "Please select a purchase from the table.")
            return

        if messagebox.askyesno("Confirm", "Delete selected purchase record?"):
            remove_purchase(self.selected_purchase)
            self.load_purchases()
            self.clear_form()

    def clear_form(self):
        self.selected_purchase = None
        self.cart = []

        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)

        self.invoice_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.today().strftime("%d-%m-%Y"))
        self.supplier_entry.set("")
        self.product_entry.set("")
        self.product_entry.configure(values=get_product_names())
        self.product_scope_label.configure(text="")
        self.quantity_entry.delete(0, "end")
        self.quantity_entry.insert(0, "1")
        self.price_entry.delete(0, "end")
        self.gst_entry.delete(0, "end")
        self.discount_entry.delete(0, "end")
        self.discount_entry.insert(0, "0")
        self.stock_preview.configure(text="")
        self.payment_status.set("Paid")
        self.on_payment_status_changed()
        self.refresh_summary()

    def load_purchases(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        rows = load_purchases()
        for row in rows:
            self.tree.insert("", "end", values=tuple(row))

    def search_purchase(self):
        keyword = self.search_entry.get().strip()

        for row in self.tree.get_children():
            self.tree.delete(row)

        if not keyword:
            self.load_purchases()
            return

        rows = find_purchase(keyword)
        for row in rows:
            self.tree.insert("", "end", values=tuple(row))

    def select_purchase(self, event):
        """
        Selecting a past purchase line just shows it for reference /
        deletion - it does not reload into the item-entry form, since
        a saved invoice can contain several lines and editing a single
        historical line in place would desync it from stock already
        applied. Use Delete + re-enter if a correction is needed.
        """
        selected = self.tree.focus()
        if not selected:
            return

        values = self.tree.item(selected)["values"]
        if not values:
            return

        self.selected_purchase = values[0]
