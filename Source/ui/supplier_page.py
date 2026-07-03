import customtkinter as ctk
from tkinter import messagebox

from assets.themes import colors
from ui.components.supplier_form import SupplierForm
from ui.components.supplier_table import SupplierTable

from services.supplier_service import (
    add_supplier,
    get_all_suppliers,
    get_supplier_by_id,
    update_supplier,
    delete_supplier,
    search_suppliers,
    find_duplicate_supplier
)
from ui.components.validators import (
    validate_name,
    validate_mobile,
    validate_email,
    run_checks
)
from ui.components.watermark import add_watermark
from ui.components.import_review_modal import pick_file_and_review


class SupplierPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        add_watermark(self)

        self.selected_supplier = None

        title = ctk.CTkLabel(
            self,
            text="🚚 Supplier Management",
            font=colors.FONT_H1,
            text_color=colors.PRIMARY
        )
        title.pack(pady=10)

        self.form = SupplierForm(self)
        self.form.pack(fill="x", padx=20)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            button_frame, text="💾 Save", width=120,
            fg_color=colors.SUCCESS, hover_color=colors.SUCCESS_HOVER,
            font=colors.FONT_BUTTON, command=self.save_supplier
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame, text="✎ Update", width=120,
            fg_color=colors.SECONDARY, hover_color=colors.SECONDARY_HOVER,
            font=colors.FONT_BUTTON, command=self.update_supplier
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame, text="🗑 Delete", width=120,
            fg_color=colors.DANGER, hover_color=colors.DANGER_HOVER,
            font=colors.FONT_BUTTON, command=self.delete_supplier
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame, text="✖ Clear", width=120,
            fg_color=colors.SIDEBAR_BUTTON,
            font=colors.FONT_BUTTON, command=self.clear_form
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame, text="📄 Import from File", width=170,
            fg_color=colors.INFO, hover_color=colors.INFO_HOVER,
            font=colors.FONT_BUTTON, command=self.import_from_file
        ).pack(side="left", padx=5)

        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20)

        self.search_entry = ctk.CTkEntry(
            search_frame, width=300,
            placeholder_text="Search by name, mobile or GST number"
        )
        self.search_entry.pack(side="left", padx=10, pady=10)

        ctk.CTkButton(
            search_frame, text="🔍 Search",
            fg_color=colors.PRIMARY, hover_color=colors.PRIMARY_HOVER,
            font=colors.FONT_BUTTON, command=self.search_supplier
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame, text="Show All",
            fg_color=colors.SIDEBAR_BUTTON,
            font=colors.FONT_BUTTON, command=self.load_suppliers
        ).pack(side="left", padx=5)

        self.table = SupplierTable(self)
        self.table.pack(fill="both", expand=True, padx=20, pady=10)

        self.table.tree.bind(
            "<<TreeviewSelect>>",
            self.select_supplier
        )

        self.load_suppliers()

    def save_supplier(self):

        name = self.form.supplier_name.get().strip()
        mobile = self.form.mobile.get().strip()
        email = self.form.email.get().strip()

        if not run_checks(
            validate_name(name, "Supplier Name"),
            validate_mobile(mobile, required=False),
            validate_email(email, required=False),
        ):
            return

        duplicate_reason = find_duplicate_supplier(name, mobile, self.form.gst_number.get())
        if duplicate_reason:
            messagebox.showwarning(
                "Duplicate Supplier",
                f"A supplier with the same {duplicate_reason} already exists. "
                f"Please check the Suppliers list, or use different details."
            )
            return

        add_supplier(
            name,
            mobile,
            self.form.gst_number.get(),
            self.form.address.get("1.0", "end").strip(),
            email
        )

        messagebox.showinfo("Success", "Supplier added successfully.")

        self.clear_form()
        self.load_suppliers()

    def load_suppliers(self):

        rows = get_all_suppliers()
        self.table.insert_rows(rows)

    def search_supplier(self):

        keyword = self.search_entry.get().strip()

        if keyword == "":
            self.load_suppliers()
            return

        rows = search_suppliers(keyword)
        self.table.insert_rows(rows)

    def select_supplier(self, event):
        """
        Loads the full details of the selected supplier back into the
        form so it can be viewed/edited (previously this only stored
        the id and never showed anything in the form fields).
        """
        selected = self.table.get_selected()

        if not selected:
            return

        self.clear_form()

        self.selected_supplier = int(selected[0])

        supplier = get_supplier_by_id(self.selected_supplier)

        if supplier is None:
            return

        self.form.supplier_name.insert(0, supplier["supplier_name"] or "")
        self.form.mobile.insert(0, supplier["mobile"] or "")
        self.form.gst_number.insert(0, supplier["gst_number"] or "")
        self.form.email.insert(0, supplier["email"] or "")
        self.form.address.insert("1.0", supplier["address"] or "")

    def update_supplier(self):

        if self.selected_supplier is None:
            messagebox.showwarning("Update", "Please select a supplier.")
            return

        name = self.form.supplier_name.get().strip()
        mobile = self.form.mobile.get().strip()
        email = self.form.email.get().strip()

        if not run_checks(
            validate_name(name, "Supplier Name"),
            validate_mobile(mobile, required=False),
            validate_email(email, required=False),
        ):
            return

        duplicate_reason = find_duplicate_supplier(
            name, mobile, self.form.gst_number.get(), exclude_id=self.selected_supplier
        )
        if duplicate_reason:
            messagebox.showwarning(
                "Duplicate Supplier",
                f"Another supplier with the same {duplicate_reason} already exists. "
                f"Please check the Suppliers list, or use different details."
            )
            return

        update_supplier(
            self.selected_supplier,
            name,
            mobile,
            self.form.gst_number.get(),
            self.form.address.get("1.0", "end").strip(),
            email
        )

        messagebox.showinfo("Success", "Supplier updated successfully.")

        self.clear_form()
        self.load_suppliers()

    def delete_supplier(self):

        if self.selected_supplier is None:
            messagebox.showwarning("Delete", "Please select a supplier.")
            return

        if messagebox.askyesno("Confirm", "Delete selected supplier?"):

            delete_supplier(self.selected_supplier)

            self.clear_form()
            self.load_suppliers()

            messagebox.showinfo("Deleted", "Supplier deleted successfully.")

    def import_from_file(self):
        def on_confirm(data):
            self.form.supplier_name.delete(0, "end")
            self.form.supplier_name.insert(0, data.get("supplier_name", ""))

            self.form.mobile.delete(0, "end")
            self.form.mobile.insert(0, data.get("mobile", ""))

            self.form.gst_number.delete(0, "end")
            self.form.gst_number.insert(0, data.get("gst_number", ""))

            self.form.email.delete(0, "end")
            self.form.email.insert(0, data.get("email", ""))

            self.form.address.delete("1.0", "end")
            self.form.address.insert("1.0", data.get("address", ""))

            messagebox.showinfo(
                "Imported",
                "Fields filled in from the file. Review them, then click Save."
            )

        pick_file_and_review(self, "supplier", on_confirm)

    def clear_form(self):

        self.selected_supplier = None

        self.form.supplier_name.delete(0, "end")
        self.form.mobile.delete(0, "end")
        self.form.gst_number.delete(0, "end")
        self.form.email.delete(0, "end")

        self.form.address.delete("1.0", "end")
