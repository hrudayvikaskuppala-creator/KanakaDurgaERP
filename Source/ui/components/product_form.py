import customtkinter as ctk


class ProductForm(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Brand
        ctk.CTkLabel(self, text="Brand").grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.brand = ctk.CTkEntry(self, width=220)
        self.brand.grid(row=0, column=1, padx=10, pady=8)

        # Model
        ctk.CTkLabel(self, text="Model").grid(row=0, column=2, padx=10, pady=8, sticky="w")
        self.model = ctk.CTkEntry(self, width=220)
        self.model.grid(row=0, column=3, padx=10, pady=8)

        # Capacity
        ctk.CTkLabel(self, text="Capacity").grid(row=1, column=0, padx=10, pady=8, sticky="w")
        self.capacity = ctk.CTkEntry(self, width=220)
        self.capacity.grid(row=1, column=1, padx=10, pady=8)

        # Purchase Price
        ctk.CTkLabel(self, text="Purchase Price").grid(row=1, column=2, padx=10, pady=8, sticky="w")
        self.purchase_price = ctk.CTkEntry(self, width=220)
        self.purchase_price.grid(row=1, column=3, padx=10, pady=8)

        # Selling Price
        ctk.CTkLabel(self, text="Selling Price").grid(row=2, column=0, padx=10, pady=8, sticky="w")
        self.selling_price = ctk.CTkEntry(self, width=220)
        self.selling_price.grid(row=2, column=1, padx=10, pady=8)

        # Warranty
        ctk.CTkLabel(self, text="Warranty (Months)").grid(row=2, column=2, padx=10, pady=8, sticky="w")
        self.warranty = ctk.CTkEntry(self, width=220)
        self.warranty.grid(row=2, column=3, padx=10, pady=8)

        # Stock
        ctk.CTkLabel(self, text="Stock").grid(row=3, column=0, padx=10, pady=8, sticky="w")
        self.stock = ctk.CTkEntry(self, width=220)
        self.stock.grid(row=3, column=1, padx=10, pady=8)

        # Minimum Stock
        ctk.CTkLabel(self, text="Minimum Stock").grid(row=3, column=2, padx=10, pady=8, sticky="w")
        self.min_stock = ctk.CTkEntry(self, width=220)
        self.min_stock.grid(row=3, column=3, padx=10, pady=8)

        # Rack Location
        ctk.CTkLabel(self, text="Rack Location").grid(row=4, column=0, padx=10, pady=8, sticky="w")
        self.rack_location = ctk.CTkEntry(self, width=220)
        self.rack_location.grid(row=4, column=1, padx=10, pady=8)

        # Barcode - click into this field and scan, or type/generate one.
        ctk.CTkLabel(self, text="Barcode").grid(row=4, column=2, padx=10, pady=8, sticky="w")
        self.barcode = ctk.CTkEntry(
            self,
            width=220,
            placeholder_text="Scan, type, or Auto-Generate"
        )
        self.barcode.grid(row=4, column=3, padx=10, pady=8)