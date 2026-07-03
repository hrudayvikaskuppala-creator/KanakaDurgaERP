import customtkinter as ctk
from tkinter import messagebox

from ui.components.product_form import ProductForm
from ui.components.product_table import ProductTable

from services.product_service import (
    add_product,
    get_all_products,
    get_product_by_id,
    update_product,
    delete_product,
    search_products,
    find_duplicate_product,
    find_duplicate_barcode,
    set_product_barcode,
    bulk_import_products
)
from ui.components.watermark import add_watermark
from ui.components.import_review_modal import pick_file_and_review
from services import barcode_service


class ProductPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        add_watermark(self)

        self.selected_product = None

        title = ctk.CTkLabel(
            self,
            text="Product Management",
            font=("Arial", 28, "bold")
        )

        title.pack(pady=15)

        self.form = ProductForm(self)
        self.form.pack(fill="x", padx=20)

        # Keyboard-wedge barcode scanners type the code then send Enter,
        # exactly like a person typing it in and pressing Enter - so this
        # is all "Import from Barcode Scanner" needs: click into the
        # field (or it already has focus after Clear) and scan.
        self.form.barcode.bind("<Return>", self._on_barcode_scanned)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            button_frame,
            text="Save",
            width=120,
            command=self.save_product
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Update",
            width=120,
            command=self.update_product
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Delete",
            width=120,
            command=self.delete_product
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Clear",
            width=120,
            command=self.clear_form
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="📊 Import (Excel/CSV/PDF)",
            width=170,
            fg_color="#0891B2",
            hover_color="#0E7490",
            command=self.import_from_file
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Generate Barcode",
            width=170,
            fg_color="#7C3AED",
            hover_color="#6D28D9",
            command=self.generate_barcode
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🖨 Print Label",
            width=140,
            fg_color="#0F766E",
            hover_color="#115E59",
            command=self.print_barcode_label
        ).pack(side="left", padx=5)

        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=20)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300
        )

        self.search_entry.pack(
            side="left",
            padx=10,
            pady=10
        )

        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_product
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Show All",
            command=self.load_products
        ).pack(side="left", padx=5)

        self.table = ProductTable(self)

        self.table.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.table.tree.bind(
            "<<TreeviewSelect>>",
            self.select_product
        )

        self.load_products()

    def save_product(self):

        if self.form.brand.get().strip() == "":
            messagebox.showwarning("Validation", "Brand is required.")
            return

        if self.form.model.get().strip() == "":
            messagebox.showwarning("Validation", "Model is required.")
            return

        brand = self.form.brand.get().strip()
        model = self.form.model.get().strip()
        capacity = self.form.capacity.get().strip()

        if find_duplicate_product(brand, model, capacity):
            messagebox.showwarning(
                "Duplicate Product",
                f"A product with the same Brand, Model and Capacity "
                f"already exists ({brand} {model} {capacity}).\n\n"
                f"Please edit that product instead, or change the details."
            )
            return

        barcode = self.form.barcode.get().strip()

        if barcode and find_duplicate_barcode(barcode):
            messagebox.showwarning(
                "Duplicate Barcode",
                f"Barcode {barcode} is already assigned to another product.\n\n"
                f"Scan/enter a different code, or use Generate Barcode."
            )
            return

        new_id = add_product(
            self.form.brand.get(),
            self.form.model.get(),
            self.form.capacity.get(),
            float(self.form.purchase_price.get() or 0),
            float(self.form.selling_price.get() or 0),
            int(self.form.warranty.get() or 0),
            int(self.form.stock.get() or 0),
            int(self.form.min_stock.get() or 0),
            self.form.rack_location.get(),
            barcode
        )

        if not barcode and new_id:
            # No barcode was scanned/typed - assign one automatically so
            # this item can still be scanned at the till right away.
            set_product_barcode(new_id, barcode_service.generate_barcode_value(new_id))

        messagebox.showinfo("Success", "Product added successfully.")

        self.clear_form()
        self.load_products()

    def load_products(self):

        rows = get_all_products()

        self.table.insert_rows(rows)

    def search_product(self):

        keyword = self.search_entry.get().strip()

        if keyword == "":
            self.load_products()
            return

        rows = search_products(keyword)

        self.table.insert_rows(rows)

    def select_product(self, event):

        selected = self.table.get_selected()

        if selected is None:
            return

        self.selected_product = int(selected[0])

        self.clear_form()

        self.selected_product = int(selected[0])

        product = get_product_by_id(self.selected_product)

        if product is None:
            return

        self.form.brand.insert(0, product["brand"])
        self.form.model.insert(0, product["model"])
        self.form.capacity.insert(0, product["capacity"] or "")
        self.form.purchase_price.insert(0, product["purchase_price"])
        self.form.selling_price.insert(0, product["selling_price"])
        self.form.warranty.insert(0, product["warranty"])
        self.form.stock.insert(0, product["stock"])
        self.form.min_stock.insert(0, product["min_stock"])
        self.form.rack_location.insert(0, product["rack_location"] or "")
        self.form.barcode.insert(0, product["barcode"] or "")

    def update_product(self):

        if self.selected_product is None:
            messagebox.showwarning(
                "Update",
                "Please select a product."
            )
            return

        brand = self.form.brand.get().strip()
        model = self.form.model.get().strip()
        capacity = self.form.capacity.get().strip()

        if find_duplicate_product(brand, model, capacity, exclude_id=self.selected_product):
            messagebox.showwarning(
                "Duplicate Product",
                f"Another product with the same Brand, Model and Capacity "
                f"already exists ({brand} {model} {capacity})."
            )
            return

        barcode = self.form.barcode.get().strip()

        if barcode and find_duplicate_barcode(barcode, exclude_id=self.selected_product):
            messagebox.showwarning(
                "Duplicate Barcode",
                f"Barcode {barcode} is already assigned to another product."
            )
            return

        update_product(
            self.selected_product,
            self.form.brand.get(),
            self.form.model.get(),
            self.form.capacity.get(),
            float(self.form.purchase_price.get() or 0),
            float(self.form.selling_price.get() or 0),
            int(self.form.warranty.get() or 0),
            int(self.form.stock.get() or 0),
            int(self.form.min_stock.get() or 0),
            self.form.rack_location.get(),
            barcode
        )

        messagebox.showinfo(
            "Success",
            "Product updated successfully."
        )

        self.clear_form()
        self.load_products()

    def delete_product(self):

        if self.selected_product is None:
            messagebox.showwarning(
                "Delete",
                "Please select a product."
            )
            return

        if messagebox.askyesno(
            "Confirm",
            "Delete selected product?"
        ):

            delete_product(self.selected_product)

            self.clear_form()
            self.load_products()

            messagebox.showinfo(
                "Deleted",
                "Product deleted successfully."
            )

    def import_from_file(self):
        def on_confirm(data):
            fields = {
                "brand": self.form.brand,
                "model": self.form.model,
                "capacity": self.form.capacity,
                "purchase_price": self.form.purchase_price,
                "selling_price": self.form.selling_price,
                "warranty": self.form.warranty,
                "rack_location": self.form.rack_location,
            }
            for key, entry in fields.items():
                entry.delete(0, "end")
                entry.insert(0, data.get(key, ""))

            messagebox.showinfo(
                "Imported",
                "Fields filled in from the file. Review them (especially "
                "prices/stock, which datasheets don't always list), then click Save."
            )

        pick_file_and_review(self, "product", on_confirm, on_bulk_confirm=self._on_bulk_products_imported)

    def _on_bulk_products_imported(self, rows):
        summary = bulk_import_products(rows)
        self.load_products()

        message = f"Added {summary['added']} new product(s), merged {summary['merged']} into existing stock."
        if summary["skipped"]:
            preview = "\n".join(summary["skipped"][:10])
            more = f"\n...and {len(summary['skipped']) - 10} more." if len(summary["skipped"]) > 10 else ""
            message += f"\n\nSkipped {len(summary['skipped'])} row(s):\n{preview}{more}"

        messagebox.showinfo("Bulk Import Complete", message)

    def _on_barcode_scanned(self, event=None):
        code = self.form.barcode.get().strip()
        if not code:
            return

        existing_id = self.selected_product
        if find_duplicate_barcode(code, exclude_id=existing_id):
            messagebox.showwarning(
                "Duplicate Barcode",
                f"Barcode {code} is already assigned to another product.\n"
                f"Scan a different label, or clear this product's barcode first."
            )
            self.form.barcode.delete(0, "end")
            self.form.barcode.focus_set()
            return

        # Valid / free to use - just leave it in the field ready for Save.
        self.form.brand.focus_set() if not self.form.brand.get().strip() else None

    def generate_barcode(self):
        """Fills the Barcode field with a fresh, unique EAN-13. Works
        whether the product is new (not yet saved) or already selected -
        either way it's just typed into the field like a scan would be,
        and only takes effect once Save/Update is clicked."""
        try:
            code = barcode_service.generate_unique_random_barcode()
        except Exception as exc:
            messagebox.showerror("Generate Barcode", str(exc))
            return

        self.form.barcode.delete(0, "end")
        self.form.barcode.insert(0, code)
        self.form.barcode.focus_set()

    def print_barcode_label(self):
        """Prints/saves a small barcode+QR label PDF for the selected
        (or currently filled-in) product."""
        brand = self.form.brand.get().strip()
        model = self.form.model.get().strip()
        code = self.form.barcode.get().strip()

        if not code:
            messagebox.showwarning(
                "Print Label",
                "This product has no barcode yet. Click Generate Barcode "
                "(or scan one into the field) first, then Save/Update."
            )
            return

        from tkinter import filedialog
        import os

        default_name = f"label_{(brand + '_' + model).strip('_').replace(' ', '_') or code}.pdf"
        save_path = filedialog.asksaveasfilename(
            title="Save Barcode Label",
            defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF label", "*.pdf")]
        )
        if not save_path:
            return

        try:
            price = self.form.selling_price.get().strip()
            barcode_service.generate_label_pdf(
                save_path,
                product_name=f"{brand} {model}".strip(),
                code=code,
                price=float(price) if price else None,
                company_name="KanakaDurga Enterprises"
            )
        except Exception as exc:
            messagebox.showerror("Print Label", f"Could not create the label:\n{exc}")
            return

        if messagebox.askyesno(
            "Label Saved",
            f"Label saved to:\n{save_path}\n\nOpen it now?"
        ):
            try:
                os.startfile(save_path)  # Windows
            except AttributeError:
                import subprocess
                import sys
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.Popen([opener, save_path])
            except Exception:
                pass

    def clear_form(self):

        self.selected_product = None

        entries = [
            self.form.brand,
            self.form.model,
            self.form.capacity,
            self.form.purchase_price,
            self.form.selling_price,
            self.form.warranty,
            self.form.stock,
            self.form.min_stock,
            self.form.rack_location,
            self.form.barcode
        ]

        for entry in entries:
            entry.delete(0, "end")