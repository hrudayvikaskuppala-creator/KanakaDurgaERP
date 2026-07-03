import tkinter as tk
from tkinter import ttk


class ProductTable(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        columns = (
            "ID",
            "Brand",
            "Model",
            "Capacity",
            "Stock",
            "Selling Price",
            "Barcode"
        )

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings",
            height=15
        )

        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=150, anchor="center")

        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert_rows(self, rows):
        self.clear()

        for row in rows:
            self.tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["brand"],
                    row["model"],
                    row["capacity"],
                    row["stock"],
                    row["selling_price"],
                    row["barcode"] or ""
                )
            )

    def get_selected(self):

        selected = self.tree.focus()

        if not selected:
            return None

        return self.tree.item(selected, "values")