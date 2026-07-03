import customtkinter as ctk


class CustomerForm(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(3, weight=1)

        self.create_widgets()

    def create_widgets(self):

        # Customer Name
        ctk.CTkLabel(self, text="Customer Name").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )

        self.customer_name = ctk.CTkEntry(self, width=250)
        self.customer_name.grid(row=0, column=1, padx=10)

        # Mobile
        ctk.CTkLabel(self, text="Mobile").grid(
            row=0, column=2, padx=10, pady=10, sticky="w"
        )

        self.mobile = ctk.CTkEntry(self, width=200)
        self.mobile.grid(row=0, column=3, padx=10)

        # WhatsApp
        ctk.CTkLabel(self, text="WhatsApp").grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )

        self.whatsapp = ctk.CTkEntry(self, width=250)
        self.whatsapp.grid(row=1, column=1, padx=10)

        # GST
        ctk.CTkLabel(self, text="GST Number").grid(
            row=1, column=2, padx=10, pady=10, sticky="w"
        )

        self.gst = ctk.CTkEntry(self, width=200)
        self.gst.grid(row=1, column=3, padx=10)

        # Address
        ctk.CTkLabel(self, text="Address").grid(
            row=2, column=0, padx=10, pady=10, sticky="w"
        )

        self.address = ctk.CTkEntry(self, width=650)
        self.address.grid(row=2, column=1, columnspan=3, padx=10, sticky="ew")

        # Vehicle Number
        ctk.CTkLabel(self, text="Vehicle Number").grid(
            row=3, column=0, padx=10, pady=10, sticky="w"
        )

        self.vehicle_number = ctk.CTkEntry(self, width=250)
        self.vehicle_number.grid(row=3, column=1, padx=10)

        # Vehicle Model
        ctk.CTkLabel(self, text="Vehicle Model").grid(
            row=3, column=2, padx=10, pady=10, sticky="w"
        )

        self.vehicle_model = ctk.CTkEntry(self, width=200)
        self.vehicle_model.grid(row=3, column=3, padx=10)

        # Email
        ctk.CTkLabel(self, text="Email").grid(
            row=4, column=0, padx=10, pady=10, sticky="w"
        )

        self.email = ctk.CTkEntry(self, width=400)
        self.email.grid(row=4, column=1, columnspan=3, padx=10, sticky="ew")