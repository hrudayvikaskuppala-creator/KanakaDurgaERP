import customtkinter as ctk

from ui.components.validators import (
    attach_text_only,
    attach_digits_only,
    attach_alnum
)


class SupplierForm(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        # Supplier Name
        ctk.CTkLabel(self, text="Supplier Name").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.supplier_name = ctk.CTkEntry(self, width=220)
        self.supplier_name.grid(row=0, column=1, padx=10)
        attach_text_only(self.supplier_name)

        # Mobile
        ctk.CTkLabel(self, text="Mobile").grid(row=0, column=2, padx=10, sticky="w")
        self.mobile = ctk.CTkEntry(self, width=220)
        self.mobile.grid(row=0, column=3, padx=10)
        attach_digits_only(self.mobile, max_len=10)

        # GST
        ctk.CTkLabel(self, text="GST Number").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.gst_number = ctk.CTkEntry(self, width=220)
        self.gst_number.grid(row=1, column=1, padx=10)
        attach_alnum(self.gst_number)

        # Email
        ctk.CTkLabel(self, text="Email").grid(row=1, column=2, padx=10, sticky="w")
        self.email = ctk.CTkEntry(self, width=220)
        self.email.grid(row=1, column=3, padx=10)

        # Address
        ctk.CTkLabel(self, text="Address").grid(row=2, column=0, padx=10, pady=8, sticky="nw")
        self.address = ctk.CTkTextbox(self, width=470, height=80)
        self.address.grid(row=2, column=1, columnspan=3, padx=10, pady=5, sticky="w")