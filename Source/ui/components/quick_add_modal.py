"""
===========================================
 Quick-Add Modals (Supplier / Product)
===========================================
Small popup windows that let the Purchase page create a brand new
supplier or product on the spot, without navigating away. This is
what powers the "single screen purchase" workflow: pick an existing
supplier/product from the dropdown, or hit "+ New" to add one in a
popup and have it selected automatically once saved.
"""

import customtkinter as ctk
from tkinter import messagebox

from assets.themes import colors
from ui.components.validators import (
    attach_text_only,
    attach_digits_only,
    attach_decimal_only,
    attach_alnum,
    validate_name,
    validate_mobile,
    validate_email,
    validate_positive_number,
    run_checks
)

from services.supplier_service import add_supplier, find_duplicate_supplier
from services.product_service import (
    add_product,
    find_duplicate_product,
    find_duplicate_barcode,
    set_product_barcode
)
from services import barcode_service
from ui.components.import_review_modal import pick_file_and_review


def _open_modal(parent, title, width=520, height=520):
    modal = ctk.CTkToplevel(parent)
    modal.title(title)
    modal.geometry(f"{width}x{height}")
    modal.resizable(False, False)
    modal.grab_set()          # modal behaviour - blocks the page behind it
    modal.transient(parent.winfo_toplevel())
    modal.configure(fg_color=colors.BACKGROUND)
    return modal


def open_quick_add_supplier(parent, on_saved):
    """
    on_saved(supplier_name) is called after a successful save so the
    caller can refresh its combobox and select the new supplier.
    """
    modal = _open_modal(parent, "New Supplier", 520, 480)

    ctk.CTkLabel(
        modal, text="➕ New Supplier", font=colors.FONT_H2, text_color=colors.PRIMARY
    ).pack(pady=(18, 10))

    card = ctk.CTkFrame(modal, fg_color=colors.CARD, corner_radius=colors.RADIUS)
    card.pack(fill="both", expand=True, padx=20, pady=10)
    card.grid_columnconfigure((0, 1), weight=1)

    def field(row, label, **kwargs):
        ctk.CTkLabel(card, text=label, font=colors.FONT_BODY_BOLD).grid(
            row=row, column=0, padx=16, pady=(14, 4), sticky="w"
        )
        entry = ctk.CTkEntry(card, width=260, **kwargs)
        entry.grid(row=row + 1, column=0, padx=16, pady=(0, 6), sticky="w")
        return entry

    name_entry = field(0, "Supplier Name *")
    attach_text_only(name_entry)

    mobile_entry = field(2, "Mobile")
    attach_digits_only(mobile_entry, max_len=10)

    gst_entry = field(4, "GST Number")
    attach_alnum(gst_entry)

    email_entry = field(6, "Email")

    ctk.CTkLabel(card, text="Address", font=colors.FONT_BODY_BOLD).grid(
        row=8, column=0, padx=16, pady=(14, 4), sticky="w"
    )
    address_box = ctk.CTkTextbox(card, width=440, height=70)
    address_box.grid(row=9, column=0, padx=16, pady=(0, 10), sticky="w")

    def import_file():
        def on_confirm(data):
            name_entry.delete(0, "end")
            name_entry.insert(0, data.get("supplier_name", ""))
            mobile_entry.delete(0, "end")
            mobile_entry.insert(0, data.get("mobile", ""))
            gst_entry.delete(0, "end")
            gst_entry.insert(0, data.get("gst_number", ""))
            email_entry.delete(0, "end")
            email_entry.insert(0, data.get("email", ""))
            address_box.delete("1.0", "end")
            address_box.insert("1.0", data.get("address", ""))

        pick_file_and_review(modal, "supplier", on_confirm)

    ctk.CTkButton(
        card, text="📄 Import from File", width=200, height=28,
        font=colors.FONT_SMALL_BOLD, fg_color=colors.INFO, hover_color=colors.INFO_HOVER,
        command=import_file
    ).grid(row=1, column=1, padx=16, pady=(14, 4), sticky="w")

    def save():
        name = name_entry.get().strip()
        mobile = mobile_entry.get().strip()
        email = email_entry.get().strip()

        if not run_checks(
            validate_name(name, "Supplier Name"),
            validate_mobile(mobile, required=False),
            validate_email(email, required=False),
        ):
            return

        duplicate_reason = find_duplicate_supplier(name, mobile, gst_entry.get().strip())
        if duplicate_reason:
            messagebox.showwarning(
                "Duplicate Supplier",
                f"A supplier with the same {duplicate_reason} already exists. "
                f"Please select them from the Supplier dropdown instead.",
                parent=modal
            )
            return

        add_supplier(
            name, mobile, gst_entry.get().strip(),
            address_box.get("1.0", "end").strip(), email
        )

        messagebox.showinfo("Success", "Supplier added.", parent=modal)
        modal.destroy()
        on_saved(name)

    button_row = ctk.CTkFrame(modal, fg_color="transparent")
    button_row.pack(pady=10)

    ctk.CTkButton(
        button_row, text="💾 Save Supplier", fg_color=colors.SUCCESS,
        hover_color=colors.SUCCESS_HOVER, font=colors.FONT_BUTTON,
        width=160, command=save
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        button_row, text="Cancel", fg_color=colors.SIDEBAR_BUTTON,
        font=colors.FONT_BUTTON, width=120, command=modal.destroy
    ).pack(side="left", padx=6)

    name_entry.focus_set()


def open_quick_add_product(parent, on_saved, prefill_barcode=None):
    """
    on_saved(product_name) is called after a successful save so the
    caller can refresh its combobox and select the new product.

    prefill_barcode: when a Sales-page scan doesn't match any existing
    product, this modal can be opened with that code pre-filled so it
    gets attached to the new product instead of being lost.
    """
    modal = _open_modal(parent, "New Product", 560, 620)

    ctk.CTkLabel(
        modal, text="➕ New Product", font=colors.FONT_H2, text_color=colors.PRIMARY
    ).pack(pady=(18, 10))

    card = ctk.CTkFrame(modal, fg_color=colors.CARD, corner_radius=colors.RADIUS)
    card.pack(fill="both", expand=True, padx=20, pady=10)

    def field(row, col, label, numeric=False, decimal=False, default=""):
        ctk.CTkLabel(card, text=label, font=colors.FONT_BODY_BOLD).grid(
            row=row, column=col, padx=14, pady=(14, 4), sticky="w"
        )
        entry = ctk.CTkEntry(card, width=200)
        entry.grid(row=row + 1, column=col, padx=14, pady=(0, 6), sticky="w")
        if default:
            entry.insert(0, default)
        if decimal:
            attach_decimal_only(entry)
        elif numeric:
            attach_digits_only(entry)
        else:
            attach_text_only(entry, allow_numbers=True)
        return entry

    brand_entry = field(0, 0, "Brand *")
    model_entry = field(0, 1, "Model *")
    capacity_entry = field(2, 0, "Capacity (Ah)")
    purchase_price_entry = field(2, 1, "Purchase Price *", decimal=True)
    selling_price_entry = field(4, 0, "Selling Price *", decimal=True)
    warranty_entry = field(4, 1, "Warranty (Months)", numeric=True)
    stock_entry = field(6, 0, "Opening Stock", numeric=True, default="0")
    min_stock_entry = field(6, 1, "Minimum Stock", numeric=True, default="0")
    rack_entry = field(8, 0, "Rack Location")
    barcode_entry = field(10, 0, "Barcode", default=prefill_barcode or "")

    def import_file():
        def on_confirm(data):
            def set_val(entry, value):
                entry.delete(0, "end")
                if value:
                    entry.insert(0, value)

            set_val(brand_entry, data.get("brand", ""))
            set_val(model_entry, data.get("model", ""))
            set_val(capacity_entry, data.get("capacity", ""))
            set_val(purchase_price_entry, data.get("purchase_price", ""))
            set_val(selling_price_entry, data.get("selling_price", ""))
            set_val(warranty_entry, data.get("warranty", ""))
            set_val(rack_entry, data.get("rack_location", ""))

        pick_file_and_review(modal, "product", on_confirm)

    ctk.CTkButton(
        card, text="📄 Import from File", width=200, height=28,
        font=colors.FONT_SMALL_BOLD, fg_color=colors.INFO, hover_color=colors.INFO_HOVER,
        command=import_file
    ).grid(row=8, column=1, padx=14, pady=(14, 4), sticky="w")

    def save():
        brand = brand_entry.get().strip()
        model = model_entry.get().strip()

        if not run_checks(
            validate_name(brand, "Brand"),
            validate_name(model, "Model", required=True),
            validate_positive_number(purchase_price_entry.get(), "Purchase Price", allow_zero=False),
            validate_positive_number(selling_price_entry.get(), "Selling Price", allow_zero=False),
        ):
            return

        capacity = capacity_entry.get().strip()
        if find_duplicate_product(brand, model, capacity):
            messagebox.showwarning(
                "Duplicate Product",
                f"A product with the same Brand, Model and Capacity already "
                f"exists ({brand} {model} {capacity}). Please select it from "
                f"the Product dropdown instead.",
                parent=modal
            )
            return

        barcode = barcode_entry.get().strip()
        if barcode and find_duplicate_barcode(barcode):
            messagebox.showwarning(
                "Duplicate Barcode",
                f"Barcode {barcode} is already assigned to another product.",
                parent=modal
            )
            return

        try:
            new_id = add_product(
                brand,
                model,
                capacity_entry.get().strip(),
                float(purchase_price_entry.get()),
                float(selling_price_entry.get()),
                int(warranty_entry.get() or 0),
                int(stock_entry.get() or 0),
                int(min_stock_entry.get() or 0),
                rack_entry.get().strip(),
                barcode
            )
        except ValueError:
            messagebox.showwarning(
                "Validation", "Please check the numeric fields.", parent=modal
            )
            return

        if not barcode and new_id:
            set_product_barcode(new_id, barcode_service.generate_barcode_value(new_id))

        product_name = f"{brand} {model}"
        messagebox.showinfo("Success", "Product added.", parent=modal)
        modal.destroy()
        on_saved(product_name)

    button_row = ctk.CTkFrame(modal, fg_color="transparent")
    button_row.pack(pady=10)

    ctk.CTkButton(
        button_row, text="💾 Save Product", fg_color=colors.SUCCESS,
        hover_color=colors.SUCCESS_HOVER, font=colors.FONT_BUTTON,
        width=160, command=save
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        button_row, text="Cancel", fg_color=colors.SIDEBAR_BUTTON,
        font=colors.FONT_BUTTON, width=120, command=modal.destroy
    ).pack(side="left", padx=6)

    brand_entry.focus_set()
