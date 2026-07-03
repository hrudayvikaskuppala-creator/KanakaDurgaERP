import customtkinter as ctk
from tkinter import messagebox

from assets.themes import colors
from ui.components.customer_form import CustomerForm
from ui.components.customer_table import CustomerTable

from services.customer_service import (
    add_customer,
    get_all_customers,
    get_customer_by_id,
    update_customer,
    delete_customer,
    search_customer,
    find_duplicate_customer
)
from ui.components.watermark import add_watermark


class CustomerPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        add_watermark(self)

        self.selected_customer = None

        title = ctk.CTkLabel(
            self,
            text="👥 Customer Management",
            font=colors.FONT_H1,
            text_color=colors.PRIMARY
        )
        title.pack(pady=10)

        # --------------------------
        # Customer Form
        # --------------------------

        self.form = CustomerForm(self)
        self.form.pack(fill="x", padx=15, pady=10)

        # --------------------------
        # Buttons
        # --------------------------

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(
            button_frame,
            text="💾 Save",
            width=120,
            fg_color=colors.SUCCESS,
            hover_color=colors.SUCCESS_HOVER,
            font=colors.FONT_BUTTON,
            command=self.save_customer
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="✎ Update",
            width=120,
            fg_color=colors.SECONDARY,
            hover_color=colors.SECONDARY_HOVER,
            font=colors.FONT_BUTTON,
            command=self.update_customer
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🗑 Delete",
            width=120,
            fg_color=colors.DANGER,
            hover_color=colors.DANGER_HOVER,
            font=colors.FONT_BUTTON,
            command=self.delete_customer
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="✖ Clear",
            width=120,
            fg_color=colors.SIDEBAR_BUTTON,
            font=colors.FONT_BUTTON,
            command=self.clear_form
        ).pack(side="left", padx=5)

        # --------------------------
        # Search
        # --------------------------

        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            search_frame,
            text="Search"
        ).pack(side="left", padx=5)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=300
        )

        self.search_entry.pack(side="left", padx=10)

        ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.search_customer
        ).pack(side="left")

        ctk.CTkButton(
            search_frame,
            text="Show All",
            command=self.load_customers
        ).pack(side="left", padx=5)

        # --------------------------
        # Customer Table
        # --------------------------

        self.table = CustomerTable(self)
        self.table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.table.tree.bind(
            "<<TreeviewSelect>>",
            self.on_row_selected
        )

        self.load_customers()

    def save_customer(self):

        name = self.form.customer_name.get().strip()
        mobile = self.form.mobile.get().strip()

        if not name:
            messagebox.showwarning(
                "Validation",
                "Customer Name is required."
            )
            return

        if find_duplicate_customer(mobile):
            messagebox.showwarning(
                "Duplicate Customer",
                f"A customer with mobile number {mobile} already exists.\n\n"
                f"Please search for them instead of adding a new record."
            )
            return

        add_customer(
            self.form.customer_name.get(),
            self.form.mobile.get(),
            self.form.whatsapp.get(),
            self.form.gst.get(),
            self.form.address.get(),
            self.form.vehicle_number.get(),
            self.form.vehicle_model.get(),
            self.form.email.get()
        )

        messagebox.showinfo(
            "Success",
            "Customer added successfully."
        )

        self.clear_form()
        self.load_customers()

    def load_customers(self):

        rows = get_all_customers()

        self.table.insert_rows(rows)

    def search_customer(self):

        keyword = self.search_entry.get().strip()

        if keyword == "":
            self.load_customers()
            return

        rows = search_customer(keyword)

        self.table.insert_rows(rows)

    def clear_form(self):

        self.selected_customer = None

        entries = [
            self.form.customer_name,
            self.form.mobile,
            self.form.whatsapp,
            self.form.gst,
            self.form.address,
            self.form.vehicle_number,
            self.form.vehicle_model,
            self.form.email
        ]

        for entry in entries:
            entry.delete(0, "end")

    def on_row_selected(self, event):

        selected = self.table.get_selected()

        if not selected:
            return

        self.selected_customer = int(selected[0])

        self.clear_form()

        self.selected_customer = int(selected[0])

        customer = get_customer_by_id(self.selected_customer)

        if customer is None:
            return

        self.form.customer_name.insert(0, customer["customer_name"] or "")
        self.form.mobile.insert(0, customer["mobile"] or "")
        self.form.whatsapp.insert(0, customer["whatsapp"] or "")
        self.form.gst.insert(0, customer["gst_number"] or "")
        self.form.address.insert(0, customer["address"] or "")
        self.form.vehicle_number.insert(0, customer["vehicle_number"] or "")
        self.form.vehicle_model.insert(0, customer["vehicle_model"] or "")
        self.form.email.insert(0, customer["email"] or "")

    def update_customer(self):

        if not self.selected_customer:
            messagebox.showwarning(
                "Update",
                "Please select a customer."
            )
            return

        mobile = self.form.mobile.get().strip()

        if find_duplicate_customer(mobile, exclude_id=self.selected_customer):
            messagebox.showwarning(
                "Duplicate Customer",
                f"Another customer with mobile number {mobile} already exists."
            )
            return

        update_customer(
            self.selected_customer,
            self.form.customer_name.get(),
            self.form.mobile.get(),
            self.form.whatsapp.get(),
            self.form.gst.get(),
            self.form.address.get(),
            self.form.vehicle_number.get(),
            self.form.vehicle_model.get(),
            self.form.email.get()
        )

        messagebox.showinfo(
            "Success",
            "Customer updated successfully."
        )

        self.clear_form()
        self.load_customers()

    def delete_customer(self):

        if not self.selected_customer:
            messagebox.showwarning(
                "Delete",
                "Please select a customer."
            )
            return

        if messagebox.askyesno(
            "Confirm",
            "Delete selected customer?"
        ):

            delete_customer(int(self.selected_customer))

            self.clear_form()
            self.load_customers()

            messagebox.showinfo(
                "Deleted",
                "Customer deleted successfully."
            )