import tkinter as tk
from tkinter import ttk


class SupplierTable(ttk.Frame):

    def __init__(self, parent):
        super().__init__(parent)

        columns = (
            "ID",
            "Supplier Name",
            "Mobile",
            "Outstanding",
            "Status"
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
        """
        Root cause of the "sqlite3.Row" text showing up in the table:
        ttk.Treeview's `values=` expects a plain tuple/list. A raw
        sqlite3.Row object isn't recognized by Tk's value marshalling,
        so it gets stringified as a whole object instead of being
        split into per-column values. Converting each row to a tuple
        here fixes it permanently (and covers any future callers of
        this table too, regardless of what data type they pass in).
        """
        self.clear()

        for row in rows:
            self.tree.insert("", "end", values=tuple(row))

    def get_selected(self):
        selected = self.tree.focus()

        if not selected:
            return None

        return self.tree.item(selected, "values")