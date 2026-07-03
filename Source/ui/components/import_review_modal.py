"""
===========================================
 Import Review Modal
===========================================
Shared "pick a file -> extract -> review -> confirm" flow used by
the Supplier page, Product page, and the Purchase page's quick-add
popups. Always shows an editable copy of whatever was extracted (never
writes straight to the database) plus the raw extracted text, so the
user can fix anything the heuristics got wrong before it's applied.
"""

from tkinter import filedialog, messagebox
import os
import customtkinter as ctk

from assets.themes import colors
from services.document_import_service import (
    extract_text_and_tables,
    extract_text_and_tables_verbose,
    parse_supplier_fields,
    parse_product_fields,
    parse_products_from_table,
    parse_invoice_fields,
    SUPPORTED_EXTENSIONS,
    BULK_EXTENSIONS,
    ImportError_
)
from services.product_service import get_product_by_brand_model_capacity

FIELD_LABELS = {
    "supplier": [
        ("supplier_name", "Supplier Name"),
        ("mobile", "Mobile"),
        ("gst_number", "GST Number"),
        ("email", "Email"),
        ("address", "Address"),
    ],
    "product": [
        ("brand", "Brand"),
        ("model", "Model"),
        ("capacity", "Capacity"),
        ("purchase_price", "Purchase Price"),
        ("selling_price", "Selling Price"),
        ("warranty", "Warranty (Months)"),
        ("rack_location", "Rack Location"),
    ],
}


def pick_file_and_review(parent, mode, on_confirm, on_bulk_confirm=None):
    """
    mode: "supplier" or "product".
    on_confirm(data: dict) is called for a single-record result (the
    usual case for a PDF/Word/image with one product/supplier on it).

    on_bulk_confirm(list_of_dicts) - if provided, and the picked file
    is a spreadsheet (xlsx/csv) or contains a multi-row product table,
    a bulk review grid is shown instead and this is called with every
    confirmed row. If omitted, only the first row is used and the
    normal single-record review opens (so existing callers that don't
    care about bulk keep working unchanged).
    """
    filetypes = [
        ("Excel / CSV (bulk import)", "*.xlsx *.csv"),
        ("PDF files", "*.pdf"),
        ("Word documents", "*.docx"),
        ("Images", "*.png *.jpg *.jpeg"),
        ("All supported files", "*.xlsx *.csv *.pdf *.docx *.png *.jpg *.jpeg"),
    ] if mode == "product" else [
        ("Supported files", "*.pdf *.docx *.png *.jpg *.jpeg"),
        ("PDF files", "*.pdf"),
        ("Word documents", "*.docx"),
        ("Images", "*.png *.jpg *.jpeg"),
    ]

    file_path = filedialog.askopenfilename(title="Import from File", filetypes=filetypes)

    if not file_path:
        return

    try:
        text, tables, confidence = extract_text_and_tables_verbose(file_path)
    except ImportError_ as exc:
        messagebox.showerror("Import Failed", str(exc), parent=parent)
        return
    except Exception as exc:
        messagebox.showerror(
            "Import Failed",
            f"Couldn't read this file.\n\nDetails: {exc}",
            parent=parent
        )
        return

    if not text.strip():
        messagebox.showwarning(
            "Nothing Found",
            "No readable text was found in this file. If it's a "
            "scanned document/photo, make sure it's clear and well-lit.",
            parent=parent
        )
        return

    if mode == "product":
        bulk_rows = []
        for table in tables:
            bulk_rows = parse_products_from_table(table)
            if bulk_rows:
                break

        is_spreadsheet = os.path.splitext(file_path)[1].lower() in BULK_EXTENSIONS

        if on_bulk_confirm and bulk_rows and (is_spreadsheet or len(bulk_rows) > 1):
            _open_bulk_product_review_modal(
                parent, bulk_rows, os.path.basename(file_path), confidence, on_bulk_confirm
            )
            return

        extracted = parse_product_fields(text, tables)
    else:
        extracted = parse_supplier_fields(text)

    _open_review_modal(parent, mode, extracted, text, on_confirm)


def _open_review_modal(parent, mode, extracted, raw_text, on_confirm):
    modal = ctk.CTkToplevel(parent)
    modal.title("Review Imported Data")
    modal.geometry("640x640")
    modal.grab_set()
    modal.transient(parent.winfo_toplevel())
    modal.configure(fg_color=colors.BACKGROUND)

    ctk.CTkLabel(
        modal, text="📄 Review Imported Data", font=colors.FONT_H2, text_color=colors.PRIMARY
    ).pack(pady=(16, 4))

    ctk.CTkLabel(
        modal,
        text="This was auto-extracted from your file - please check it's\ncorrect (and fill anything left blank) before using it.",
        font=colors.FONT_SMALL, text_color=colors.TEXT_LIGHT, justify="center"
    ).pack(pady=(0, 10))

    scroll = ctk.CTkScrollableFrame(modal, fg_color=colors.CARD, corner_radius=colors.RADIUS)
    scroll.pack(fill="both", expand=True, padx=20, pady=6)
    scroll.grid_columnconfigure(1, weight=1)

    entries = {}
    for row, (key, label) in enumerate(FIELD_LABELS[mode]):
        ctk.CTkLabel(scroll, text=label, font=colors.FONT_BODY_BOLD).grid(
            row=row, column=0, padx=12, pady=8, sticky="w"
        )
        entry = ctk.CTkEntry(scroll, width=380)
        entry.grid(row=row, column=1, padx=12, pady=8, sticky="ew")
        entry.insert(0, extracted.get(key, "") or "")
        entries[key] = entry

    with_raw_row = len(FIELD_LABELS[mode])
    ctk.CTkLabel(scroll, text="Raw extracted text", font=colors.FONT_BODY_BOLD).grid(
        row=with_raw_row, column=0, columnspan=2, padx=12, pady=(16, 4), sticky="w"
    )
    raw_box = ctk.CTkTextbox(scroll, width=560, height=140)
    raw_box.grid(row=with_raw_row + 1, column=0, columnspan=2, padx=12, pady=(0, 10), sticky="ew")
    raw_box.insert("1.0", raw_text.strip()[:4000])
    raw_box.configure(state="disabled")

    def confirm():
        data = {key: entry.get().strip() for key, entry in entries.items()}
        modal.destroy()
        on_confirm(data)

    button_row = ctk.CTkFrame(modal, fg_color="transparent")
    button_row.pack(pady=12)

    ctk.CTkButton(
        button_row, text="✅ Use This Data", fg_color=colors.SUCCESS,
        hover_color=colors.SUCCESS_HOVER, font=colors.FONT_BUTTON,
        width=180, command=confirm
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        button_row, text="Cancel", fg_color=colors.SIDEBAR_BUTTON,
        font=colors.FONT_BUTTON, width=120, command=modal.destroy
    ).pack(side="left", padx=6)


# ---------------------------------------------------------------------------
# Bulk product import (xlsx/csv/multi-row table) - editable preview grid,
# with duplicate detection so existing products get merged (stock added,
# price refreshed) instead of being re-created.
# ---------------------------------------------------------------------------

# Tkinter renders every cell as a real widget, so a many-thousand-row
# grid would be very slow to build and scroll. This caps how many rows
# get individual editable widgets; every row beyond it still gets
# imported (using its auto-extracted values, unedited) - just not
# rendered for inline editing. The cap only affects the *preview*, not
# how many records can actually be imported in one go.
MAX_EDITABLE_PREVIEW_ROWS = 250

CONFIDENCE_LABELS = {
    "table": ("✅ Read from a real table - high confidence", colors.SUCCESS),
    "text": ("ℹ️ Read from plain text (no table found) - please double-check", colors.WARNING),
    "ocr": ("⚠️ Read using OCR (scanned/photo) - please verify carefully", colors.DANGER),
}


def _open_bulk_product_review_modal(parent, rows, source_filename, confidence, on_bulk_confirm):
    modal = ctk.CTkToplevel(parent)
    modal.title("Review Bulk Product Import")
    modal.geometry("1000x700")
    modal.grab_set()
    modal.transient(parent.winfo_toplevel())
    modal.configure(fg_color=colors.BACKGROUND)

    ctk.CTkLabel(
        modal, text=f"📊 Bulk Import Preview — {len(rows)} row(s) found in {source_filename}",
        font=colors.FONT_H2, text_color=colors.PRIMARY
    ).pack(pady=(16, 4))

    conf_text, conf_color = CONFIDENCE_LABELS.get(confidence, CONFIDENCE_LABELS["text"])
    ctk.CTkLabel(modal, text=conf_text, font=colors.FONT_BODY_BOLD, text_color=conf_color).pack(pady=(0, 8))

    if len(rows) > MAX_EDITABLE_PREVIEW_ROWS:
        ctk.CTkLabel(
            modal,
            text=(
                f"Showing the first {MAX_EDITABLE_PREVIEW_ROWS} rows for editing. The remaining "
                f"{len(rows) - MAX_EDITABLE_PREVIEW_ROWS} will still be imported using their "
                f"auto-extracted values as-is - fix the source file first if something looks wrong here."
            ),
            font=colors.FONT_SMALL, text_color=colors.TEXT_LIGHT, wraplength=900, justify="center"
        ).pack(pady=(0, 8))

    outer = ctk.CTkScrollableFrame(modal, fg_color="transparent")
    outer.pack(fill="both", expand=True, padx=16, pady=6)

    headers = ("Include", "Brand", "Model", "Capacity", "Purch. Price", "Sell Price", "Warranty", "Stock", "Rack", "Status")
    header_row_frame = ctk.CTkFrame(outer, fg_color=colors.CARD, corner_radius=colors.RADIUS_SM)
    header_row_frame.pack(fill="x", pady=(0, 4))
    for col, text in enumerate(headers):
        header_row_frame.grid_columnconfigure(col, weight=1 if col == 9 else 0)
        ctk.CTkLabel(header_row_frame, text=text, font=colors.FONT_SMALL_BOLD).grid(
            row=0, column=col, padx=6, pady=6, sticky="w"
        )

    fields = ("brand", "model", "capacity", "purchase_price", "selling_price", "warranty", "stock", "rack_location")
    widths = (110, 110, 80, 90, 90, 70, 60, 90)

    row_widgets = []
    editable_rows = rows[:MAX_EDITABLE_PREVIEW_ROWS]
    overflow_rows = rows[MAX_EDITABLE_PREVIEW_ROWS:]

    for r, row in enumerate(editable_rows):
        row_frame = ctk.CTkFrame(outer, fg_color="transparent")
        row_frame.pack(fill="x", pady=1)

        include_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(row_frame, text="", variable=include_var, width=20).grid(row=0, column=0, padx=6)

        entries = {}
        for col, (field, width) in enumerate(zip(fields, widths), start=1):
            entry = ctk.CTkEntry(row_frame, width=width)
            entry.insert(0, str(row.get(field, "") or ""))
            entry.grid(row=0, column=col, padx=3)
            entries[field] = entry

        existing = get_product_by_brand_model_capacity(
            row.get("brand", ""), row.get("model", ""), row.get("capacity", "")
        )
        if existing:
            status_text, status_color = f"↻ Will merge into #{existing['id']}", colors.WARNING
        elif not row.get("brand") or not row.get("model"):
            status_text, status_color = "⚠ Needs Brand + Model", colors.DANGER
        else:
            status_text, status_color = "＋ New product", colors.SUCCESS

        status_label = ctk.CTkLabel(row_frame, text=status_text, font=colors.FONT_SMALL, text_color=status_color)
        status_label.grid(row=0, column=9, padx=6, sticky="w")

        row_widgets.append((include_var, entries))

    def confirm():
        confirmed = []
        skipped_invalid = 0

        for include_var, entries in row_widgets:
            if not include_var.get():
                continue
            data = {field: entry.get().strip() for field, entry in entries.items()}
            if not data.get("brand") or not data.get("model"):
                skipped_invalid += 1
                continue
            confirmed.append(data)

        confirmed.extend(overflow_rows)  # already validated to have brand/model earlier

        if not confirmed:
            messagebox.showwarning(
                "Nothing to Import", "No valid rows are selected (Brand and Model are required).",
                parent=modal
            )
            return

        modal.destroy()
        on_bulk_confirm(confirmed)

        if skipped_invalid:
            messagebox.showinfo(
                "Some Rows Skipped",
                f"{skipped_invalid} row(s) were skipped for missing Brand/Model."
            )

    button_row = ctk.CTkFrame(modal, fg_color="transparent")
    button_row.pack(pady=12)

    ctk.CTkButton(
        button_row, text=f"✅ Import Selected Products", fg_color=colors.SUCCESS,
        hover_color=colors.SUCCESS_HOVER, font=colors.FONT_BUTTON,
        width=220, command=confirm
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        button_row, text="Cancel", fg_color=colors.SIDEBAR_BUTTON,
        font=colors.FONT_BUTTON, width=120, command=modal.destroy
    ).pack(side="left", padx=6)


# ---------------------------------------------------------------------------
# Purchase invoice import (multi line-item) - used by the Purchase page.
# ---------------------------------------------------------------------------

INVOICE_FIELD_LABELS = [
    ("supplier_name", "Supplier Name"),
    ("mobile", "Supplier Mobile"),
    ("gst_number", "Supplier GST Number"),
    ("address", "Supplier Address"),
    ("invoice_no", "Invoice No"),
    ("date", "Date"),
]


def pick_invoice_and_review(parent, on_confirm):
    """
    Lets the user pick a supplier's purchase invoice (PDF/scanned image/
    Word doc), extracts the supplier details plus every product line
    item it can find (table-based when the document has one, otherwise
    a conservative text pattern match), and shows an editable review
    before anything touches the database.

    on_confirm(supplier_data: dict, invoice_no: str, date: str,
               line_items: list[dict with product/qty/price/gst]) is
    called once the user confirms - nothing is written here, the
    Purchase page decides how to apply it (match/create products,
    add to the current cart, etc).
    """
    file_path = filedialog.askopenfilename(
        title="Import Purchase Invoice",
        filetypes=[
            ("Supported files", "*.pdf *.docx *.png *.jpg *.jpeg"),
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("Images (scanned invoice)", "*.png *.jpg *.jpeg"),
        ]
    )

    if not file_path:
        return

    try:
        text, tables = extract_text_and_tables(file_path)
    except ImportError_ as exc:
        messagebox.showerror("Import Failed", str(exc), parent=parent)
        return
    except Exception as exc:
        messagebox.showerror(
            "Import Failed", f"Couldn't read this file.\n\nDetails: {exc}", parent=parent
        )
        return

    if not text.strip():
        messagebox.showwarning(
            "Nothing Found",
            "No readable text was found in this file. If it's a scanned "
            "document/photo, make sure it's clear and well-lit.",
            parent=parent
        )
        return

    extracted = parse_invoice_fields(text, tables)
    _open_invoice_review_modal(parent, extracted, text, on_confirm)


def _open_invoice_review_modal(parent, extracted, raw_text, on_confirm):
    modal = ctk.CTkToplevel(parent)
    modal.title("Review Imported Invoice")
    modal.geometry("820x680")
    modal.grab_set()
    modal.transient(parent.winfo_toplevel())
    modal.configure(fg_color=colors.BACKGROUND)

    ctk.CTkLabel(
        modal, text="📄 Review Imported Invoice", font=colors.FONT_H2, text_color=colors.PRIMARY
    ).pack(pady=(16, 4))

    ctk.CTkLabel(
        modal,
        text="Check the supplier details and line items below (edit anything the\n"
             "extraction got wrong, and untick any row you don't want to import).",
        font=colors.FONT_SMALL, text_color=colors.TEXT_LIGHT, justify="center"
    ).pack(pady=(0, 10))

    outer = ctk.CTkScrollableFrame(modal, fg_color="transparent")
    outer.pack(fill="both", expand=True, padx=20, pady=6)

    header_card = ctk.CTkFrame(outer, fg_color=colors.CARD, corner_radius=colors.RADIUS)
    header_card.pack(fill="x", pady=(0, 12))
    header_card.grid_columnconfigure(1, weight=1)

    header_entries = {}
    for row, (key, label) in enumerate(INVOICE_FIELD_LABELS):
        ctk.CTkLabel(header_card, text=label, font=colors.FONT_BODY_BOLD).grid(
            row=row, column=0, padx=12, pady=8, sticky="w"
        )
        entry = ctk.CTkEntry(header_card, width=380)
        entry.grid(row=row, column=1, padx=12, pady=8, sticky="ew")
        entry.insert(0, extracted.get(key, "") or "")
        header_entries[key] = entry

    items_label = ctk.CTkLabel(
        outer,
        text=f"Line Items ({len(extracted.get('line_items', []))} found)",
        font=colors.FONT_H3, text_color=colors.PRIMARY
    )
    items_label.pack(anchor="w", pady=(4, 6))

    items_card = ctk.CTkFrame(outer, fg_color=colors.CARD, corner_radius=colors.RADIUS)
    items_card.pack(fill="x", pady=(0, 12))

    col_headers = ("Include", "Product", "Qty", "Price", "GST %")
    for col, text in enumerate(col_headers):
        ctk.CTkLabel(items_card, text=text, font=colors.FONT_BODY_BOLD).grid(
            row=0, column=col, padx=8, pady=(10, 6), sticky="w"
        )

    row_widgets = []
    line_items = extracted.get("line_items", [])

    if not line_items:
        ctk.CTkLabel(
            items_card,
            text="No line items were detected automatically. You can still use the\n"
                 "supplier/invoice details above and add products manually below.",
            font=colors.FONT_SMALL, text_color=colors.TEXT_LIGHT, justify="left"
        ).grid(row=1, column=0, columnspan=5, padx=8, pady=10, sticky="w")

    for r, item in enumerate(line_items, start=1):
        include_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(items_card, text="", variable=include_var, width=20).grid(
            row=r, column=0, padx=8, pady=4
        )

        product_entry = ctk.CTkEntry(items_card, width=220)
        product_entry.insert(0, str(item.get("product", "")))
        product_entry.grid(row=r, column=1, padx=6, pady=4, sticky="w")

        qty_entry = ctk.CTkEntry(items_card, width=70)
        qty_entry.insert(0, str(item.get("qty", "") or ""))
        qty_entry.grid(row=r, column=2, padx=6, pady=4, sticky="w")

        price_entry = ctk.CTkEntry(items_card, width=90)
        price_entry.insert(0, str(item.get("price", "") or ""))
        price_entry.grid(row=r, column=3, padx=6, pady=4, sticky="w")

        gst_entry = ctk.CTkEntry(items_card, width=70)
        gst_entry.insert(0, str(item.get("gst", "") or ""))
        gst_entry.grid(row=r, column=4, padx=6, pady=4, sticky="w")

        row_widgets.append((include_var, product_entry, qty_entry, price_entry, gst_entry))

    def confirm():
        supplier_data = {
            key: entry.get().strip()
            for key, entry in header_entries.items()
            if key not in ("invoice_no", "date")
        }
        invoice_no = header_entries["invoice_no"].get().strip()
        date = header_entries["date"].get().strip()

        confirmed_items = []
        for include_var, product_entry, qty_entry, price_entry, gst_entry in row_widgets:
            if not include_var.get():
                continue
            product_name = product_entry.get().strip()
            if not product_name:
                continue

            def _to_float(entry, default=0.0):
                try:
                    return float(entry.get().strip() or default)
                except ValueError:
                    return default

            confirmed_items.append({
                "product": product_name,
                "qty": _to_float(qty_entry, 1),
                "price": _to_float(price_entry, 0),
                "gst": _to_float(gst_entry, 0),
            })

        modal.destroy()
        on_confirm(supplier_data, invoice_no, date, confirmed_items)

    button_row = ctk.CTkFrame(modal, fg_color="transparent")
    button_row.pack(pady=12)

    ctk.CTkButton(
        button_row, text="✅ Import Selected Items", fg_color=colors.SUCCESS,
        hover_color=colors.SUCCESS_HOVER, font=colors.FONT_BUTTON,
        width=200, command=confirm
    ).pack(side="left", padx=6)

    ctk.CTkButton(
        button_row, text="Cancel", fg_color=colors.SIDEBAR_BUTTON,
        font=colors.FONT_BUTTON, width=120, command=modal.destroy
    ).pack(side="left", padx=6)
