import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from assets.themes import colors
from services.invoice_service import (
    generate_invoice_number,
    get_current_date,
    get_current_time
)
from services.sales_service import add_sale, load_sales, invoice_number_exists
from services.campany_service import get_company
from services.pos.manager import requires_pos
from services.pos_transaction_service import record_transaction
from ui.components.pos_terminal_modal import open_pos_terminal
from ui.components.quick_add_modal import open_quick_add_product
from models.customer import get_customer_names
from models.product import get_product_names, get_product_details, decrease_stock
from services import barcode_service
from ui.components.watermark import add_watermark


class SalesPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        add_watermark(self)

        self.last_sale = None

        self.create_widgets()
        self.load_sales()
        self.barcode_entry.focus_set()

    def create_widgets(self):

        title = ctk.CTkLabel(
            self,
            text="🧾 Sales Invoice",
            font=colors.FONT_H1,
            text_color=colors.PRIMARY
        )
        title.pack(pady=15)

        # ---------------- Barcode Scanner ----------------
        # A keyboard-wedge scanner just "types" the code into whatever
        # field has focus and sends Enter - so this field only needs to
        # stay focused for scanning to work with no button click at all.
        scan_frame = ctk.CTkFrame(self, fg_color=colors.CARD, corner_radius=colors.RADIUS_SM)
        scan_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            scan_frame,
            text="🔍 Scan Barcode",
            font=colors.FONT_BODY_BOLD
        ).pack(side="left", padx=(15, 8), pady=10)

        self.barcode_entry = ctk.CTkEntry(
            scan_frame,
            width=280,
            placeholder_text="Click here, then scan (or type a code and press Enter)"
        )
        self.barcode_entry.pack(side="left", padx=8, pady=10)
        self.barcode_entry.bind("<Return>", self.on_barcode_scanned)

        self.scan_status_label = ctk.CTkLabel(scan_frame, text="", font=colors.FONT_SMALL)
        self.scan_status_label.pack(side="left", padx=10)

        form = ctk.CTkFrame(self)
        form.pack(fill="x", padx=20, pady=10)

        # ---------------- Row 1 ----------------

        ctk.CTkLabel(
            form,
            text="Invoice No"
        ).grid(row=0, column=0, padx=10, pady=8)

        self.invoice_entry = ctk.CTkEntry(
            form,
            width=180
        )
        self.invoice_entry.grid(row=0, column=1)
        self.invoice_entry.insert(
            0,
            generate_invoice_number()
        )

        ctk.CTkLabel(
            form,
            text="Date"
        ).grid(row=0, column=2)

        self.date_entry = ctk.CTkEntry(
            form,
            width=180
        )
        self.date_entry.grid(row=0, column=3)
        self.date_entry.insert(0, get_current_date())

        # Time
        ctk.CTkLabel(
            form,
            text="Time"
        ).grid(row=0, column=4, padx=10)

        self.time_entry = ctk.CTkEntry(
            form,
            width=150
        )
        self.time_entry.grid(row=0, column=5)
        self.time_entry.insert(0, get_current_time())


        # ---------------- Row 2 ----------------

        ctk.CTkLabel(
            form,
            text="Customer Type"
        ).grid(row=1, column=0, padx=10)

        self.customer_type = ctk.CTkOptionMenu(
            form,
            values=[
                "Walk-in",
                "Registered Customer"
            ],
            command=self.customer_type_changed
        )

        self.customer_type.grid(
            row=1,
            column=1,
            padx=5
        )

        self.customer_type.set("Walk-in")


        ctk.CTkLabel(
            form,
            text="Customer"
        ).grid(row=1, column=2, padx=10)

        self.customer_combo = ctk.CTkComboBox(
            form,
            width=250,
            values=get_customer_names()
        )

        self.customer_combo.grid(row=1, column=3)

        self.customer_combo.set("Cash Customer (Walk-in)")
        self.customer_combo.configure(state="disabled")  # avoid CTk showing its own class name when values is empty

        ctk.CTkButton(
            form,
            text="+ Customer",
            width=110,
            height=colors.BUTTON_HEIGHT,
            corner_radius=colors.RADIUS_SM,
            font=colors.FONT_BUTTON,
            fg_color=colors.PRIMARY,
            hover_color=colors.PRIMARY_HOVER,
            command=self.open_customer_page
        ).grid(
            row=1,
            column=4,
            padx=(5, 10),
            pady=5,
            sticky="w"
        )
        ctk.CTkLabel(
            form,
            text="Product"
        ).grid(row=1, column=2)

        self.product_combo = ctk.CTkComboBox(
            form,
            width=250,
            values=get_product_names(),
            command=self.load_product_details
        )
        self.product_combo.grid(row=1, column=3)
        self.product_combo.set("")  # avoid CTk showing its own class name when values is empty

# ---------------- Row 3 ----------------

        ctk.CTkLabel(
            form,
            text="Quantity"
        ).grid(row=2, column=0, padx=10)

        self.quantity_entry = ctk.CTkEntry(
            form,
            width=180
        )
        self.quantity_entry.grid(row=2, column=1)
        self.quantity_entry.bind(
            "<KeyRelease>",
            lambda e: self.calculate_total()
        )

        ctk.CTkLabel(
            form,
            text="Selling Price"
        ).grid(row=2, column=2)

        self.price_entry = ctk.CTkEntry(
            form,
            width=180
        )
        self.price_entry.grid(row=2, column=3)
        self.price_entry.bind(
            "<KeyRelease>",
            lambda e: self.calculate_total()
        )

        # ---------------- Row 4 ----------------

        ctk.CTkLabel(
            form,
            text="GST %"
        ).grid(row=3, column=0)

        self.gst_entry = ctk.CTkEntry(
            form,
            width=180
        )
        self.gst_entry.insert(0, "18")
        self.gst_entry.grid(row=3, column=1)
        self.gst_entry.bind(
            "<KeyRelease>",
            lambda e: self.calculate_total()
        )

        ctk.CTkLabel(
            form,
            text="Discount"
        ).grid(row=3, column=2)

        self.discount_entry = ctk.CTkEntry(
            form,
            width=180
        )
        self.discount_entry.insert(0, "0")
        self.discount_entry.grid(row=3, column=3)
        self.discount_entry.bind(
            "<KeyRelease>",
            lambda e: self.calculate_total()
        )

        # ---------------- Row 5 ----------------

        ctk.CTkLabel(
            form,
            text="Payment Mode"
        ).grid(row=4, column=0)

        self.payment_combo = ctk.CTkComboBox(
            form,
            width=180,
            values=[
                "Cash",
                "UPI",
                "Credit Card",
                "Debit Card",
                "QR Code",
                "Bank Transfer",
                "Credit"
            ]
        )
        self.payment_combo.grid(row=4, column=1)
        self.payment_combo.set("Cash")

        ctk.CTkLabel(
            form,
            text="Total"
        ).grid(row=4, column=2)

        self.total_entry = ctk.CTkEntry(
            form,
            width=180
        )
        self.total_entry.grid(row=4, column=3)

        # ---------------- Row 6 - Warranty ----------------

        ctk.CTkLabel(
            form,
            text="Warranty Type"
        ).grid(row=5, column=0)

        self.warranty_combo = ctk.CTkComboBox(
            form,
            width=180,
            values=[
                "Comprehensive",
                "Pro-Rata",
                "Comprehensive + Pro-Rata",
                "No Warranty"
            ]
        )
        self.warranty_combo.grid(row=5, column=1)
        self.warranty_combo.set("Comprehensive")

        # ---------------- Buttons ----------------

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=15)

        ctk.CTkButton(
            button_frame,
            text="💾 Save Sale",
            width=150,
            height=colors.BUTTON_HEIGHT,
            corner_radius=colors.RADIUS_SM,
            font=colors.FONT_BUTTON,
            fg_color=colors.SUCCESS,
            hover_color=colors.SUCCESS_HOVER,
            command=self.save_sale
        ).grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            button_frame,
            text="🖨 Print Invoice",
            width=150,
            height=colors.BUTTON_HEIGHT,
            corner_radius=colors.RADIUS_SM,
            font=colors.FONT_BUTTON,
            fg_color=colors.SECONDARY,
            hover_color=colors.SECONDARY_HOVER,
            command=self.print_invoice
        ).grid(row=0, column=1, padx=5)

        ctk.CTkButton(
            button_frame,
            text="✖ Clear",
            width=150,
            height=colors.BUTTON_HEIGHT,
            corner_radius=colors.RADIUS_SM,
            font=colors.FONT_BUTTON,
            fg_color=colors.SIDEBAR_BUTTON,
            hover_color=colors.DANGER,
            command=self.clear_form
        ).grid(row=0, column=2, padx=5)

        # ---------------- Sales Table ----------------

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        columns = (
            "Invoice",
            "Date",
            "Customer",
            "Product",
            "Qty",
            "Total",
            "Payment",
            "Warranty"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140)

        self.tree.pack(
            fill="both",
            expand=True
        )
    def calculate_total(self):
        try:
            qty = float(self.quantity_entry.get() or 0)
            price = float(self.price_entry.get() or 0)
            gst = float(self.gst_entry.get() or 0)
            discount = float(self.discount_entry.get() or 0)

            subtotal = qty * price
            gst_amount = subtotal * gst / 100

            total = subtotal + gst_amount - discount

            self.total_entry.delete(0, "end")
            self.total_entry.insert(0, f"{total:.2f}")

        except ValueError:
            self.total_entry.delete(0, "end")

    def clear_form(self):

        self.invoice_entry.delete(0, "end")
        self.invoice_entry.insert(
            0,
            generate_invoice_number()
        )

        self.date_entry.delete(0, "end")
        self.date_entry.insert(
            0,
            get_current_date()
        )

        self.customer_combo.set("")
        self.product_combo.set("")

        self.quantity_entry.delete(0, "end")
        self.price_entry.delete(0, "end")

        self.gst_entry.delete(0, "end")
        self.gst_entry.insert(0, "18")

        self.discount_entry.delete(0, "end")
        self.discount_entry.insert(0, "0")

        self.total_entry.delete(0, "end")

        self.payment_combo.set("Cash")
        self.warranty_combo.set("Comprehensive")

        self.barcode_entry.delete(0, "end")
        self.scan_status_label.configure(text="")
        self.barcode_entry.focus_set()

    def open_customer_page(self):

        from ui.customer_page import CustomerPage

        window = ctk.CTkToplevel(self)
        window.title("Customer Management")
        window.geometry("1200x750")

        CustomerPage(window) 


    def save_sale(self):

        try:

            invoice = self.invoice_entry.get()
            sale_date = self.date_entry.get()
            customer = self.customer_combo.get()
            product = self.product_combo.get()

            if invoice_number_exists(invoice):
                messagebox.showwarning(
                    "Duplicate Invoice",
                    f"Invoice '{invoice}' has already been saved. Please use "
                    f"a different invoice number."
                )
                return

            quantity = int(self.quantity_entry.get())

            selling_price = float(self.price_entry.get())

            gst = float(self.gst_entry.get())

            discount = float(self.discount_entry.get())

            payment = self.payment_combo.get()
            warranty_type = self.warranty_combo.get()

            subtotal = quantity * selling_price
            gst_amount = subtotal * gst / 100

            total = subtotal + gst_amount - discount

            sale_data = {
                "invoice": invoice,
                "date": sale_date,
                "time": self.time_entry.get(),
                "customer": customer,
                "product": product,
                "quantity": quantity,
                "selling_price": selling_price,
                "gst": gst,
                "discount": discount,
                "total": total,
                "payment": payment,
                "warranty_type": warranty_type,
            }

            if requires_pos(payment):
                self._charge_via_pos(sale_data)
            else:
                self._finalize_sale(sale_data)

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    def customer_type_changed(self, value):

        if value == "Walk-in":
            self.customer_combo.set("Cash Customer (Walk-in)")
            self.customer_combo.configure(state="disabled")

        else:
            self.customer_combo.configure(state="normal")
            self.customer_combo.configure(values=get_customer_names())
            self.customer_combo.set("")

    def _charge_via_pos(self, sale_data):
        """
        Opens the POS terminal modal for digital payment modes. The
        sale is only ever written to the database from
        on_success/on_failure below - nothing is saved just because
        the user clicked Save, which is what keeps a declined/
        cancelled payment from ever touching stock or invoice records.
        """

        def on_success(result, provider_name):
            record_transaction(
                sale_data["invoice"], sale_data["total"], sale_data["payment"],
                provider_name, result
            )
            self._finalize_sale(sale_data, pos_result=result, auto_print=True)

        def on_failure(result, provider_name):
            record_transaction(
                sale_data["invoice"], sale_data["total"], sale_data["payment"],
                provider_name, result
            )

            retry = messagebox.askretrycancel(
                "Payment Not Completed",
                f"{result.message}\n\nThe sale has NOT been saved and stock has "
                f"NOT been changed. Would you like to try the payment again?"
            )
            if retry:
                self._charge_via_pos(sale_data)

        open_pos_terminal(
            self, sale_data["total"], sale_data["payment"], sale_data["invoice"],
            on_success, on_failure
        )

    def _finalize_sale(self, sale_data, pos_result=None, auto_print=False):
        """
        The single place that actually writes a sale to the database.
        Called directly for Cash/Bank Transfer/Credit, and only after
        a confirmed POS approval for digital payment modes.
        """
        add_sale(
            sale_data["invoice"],
            sale_data["date"],
            sale_data["customer"],
            sale_data["product"],
            sale_data["quantity"],
            sale_data["selling_price"],
            sale_data["gst"],
            sale_data["discount"],
            sale_data["total"],
            sale_data["payment"],
            sale_data["warranty_type"]
        )

        decrease_stock(sale_data["product"], sale_data["quantity"])

        self.last_sale = dict(sale_data)
        if pos_result:
            self.last_sale["pos_transaction_id"] = pos_result.transaction_id
            self.last_sale["pos_approval_code"] = pos_result.approval_code

        if pos_result:
            messagebox.showinfo(
                "Payment Approved",
                f"{pos_result.message}\n\nSale saved, stock updated, and this "
                f"invoice is marked Paid."
            )
        else:
            messagebox.showinfo("Success", "Sale saved successfully.")

        self.clear_form()
        self.load_sales()

        if auto_print:
            self.print_invoice()

    def load_sales(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        for sale in load_sales():
            self.tree.insert(
                "",
                "end",
                values=(
                    sale["invoice_no"],
                    sale["sale_date"],
                    sale["customer"],
                    sale["product"],
                    sale["quantity"],
                    sale["total"],
                    sale["payment_mode"],
                    sale["warranty_type"]
                )
            )

    def load_product_details(self, product_name):

        data = get_product_details(product_name)

        if not data:
            return

        self.price_entry.delete(0, "end")
        self.price_entry.insert(0, str(data["selling_price"]))

    def on_barcode_scanned(self, event=None):
        """
        Handles a scan (or a typed code + Enter) in the barcode field.

        Note on scope: this Sales invoice currently holds one product
        line at a time (there's no multi-row cart yet), so "continuous
        scanning" here means: scanning the *same* item again bumps its
        quantity by 1 (handy for grabbing several units of one battery
        off the shelf), while scanning a *different* item replaces the
        current selection after a confirmation, so nothing gets lost by
        accident. A true multi-line cart is a bigger, separate change.
        """
        code = self.barcode_entry.get().strip()
        self.barcode_entry.delete(0, "end")

        if not code:
            return

        product = barcode_service.lookup_product_by_code(code)

        if product is None:
            self.scan_status_label.configure(
                text=f"⚠ No product found for {code}", text_color=colors.WARNING
            )
            if messagebox.askyesno(
                "Barcode Not Found",
                f"No product is linked to barcode {code}.\n\n"
                f"Create a new product for this code now?"
            ):
                def on_saved(product_name):
                    self.product_combo.configure(values=get_product_names())
                    self.product_combo.set(product_name)
                    self.load_product_details(product_name)
                    self.barcode_entry.focus_set()

                open_quick_add_product(self, on_saved, prefill_barcode=code)
            else:
                self.barcode_entry.focus_set()
            return

        product_name = f"{product['brand']} {product['model']}"
        current_qty = self.quantity_entry.get().strip()

        if self.product_combo.get().strip() == product_name and current_qty:
            # Same item scanned again - treat it as another unit.
            try:
                self.quantity_entry.delete(0, "end")
                self.quantity_entry.insert(0, str(int(float(current_qty)) + 1))
            except ValueError:
                self.quantity_entry.delete(0, "end")
                self.quantity_entry.insert(0, "1")
        else:
            self.product_combo.configure(values=get_product_names())
            self.product_combo.set(product_name)
            self.load_product_details(product_name)
            if not current_qty:
                self.quantity_entry.delete(0, "end")
                self.quantity_entry.insert(0, "1")

        self.calculate_total()

        if product["stock"] is not None and product["stock"] <= 0:
            self.scan_status_label.configure(
                text=f"⚠ {product_name} is OUT OF STOCK", text_color=colors.DANGER
            )
        else:
            self.scan_status_label.configure(
                text=f"✓ {product_name} — stock: {product['stock']}",
                text_color=colors.SUCCESS
            )

        self.barcode_entry.focus_set()

    def print_invoice(self):
        """
        Build a printable receipt for the last saved sale (falls back
        to the currently filled-in form if nothing was saved yet) and
        show it in a preview window with a Save-to-file option.
        """
        sale = self.last_sale

        if not sale:
            # Fall back to whatever is currently in the form so the
            # user can preview an invoice before saving.
            try:
                quantity = int(self.quantity_entry.get() or 0)
                selling_price = float(self.price_entry.get() or 0)
                gst = float(self.gst_entry.get() or 0)
                discount = float(self.discount_entry.get() or 0)
                subtotal = quantity * selling_price
                total = subtotal + (subtotal * gst / 100) - discount
            except ValueError:
                messagebox.showwarning(
                    "Print Invoice",
                    "Please fill in valid sale details, or save a "
                    "sale first."
                )
                return

            sale = {
                "invoice": self.invoice_entry.get(),
                "date": self.date_entry.get(),
                "time": self.time_entry.get(),
                "customer": self.customer_combo.get(),
                "product": self.product_combo.get(),
                "quantity": quantity,
                "selling_price": selling_price,
                "gst": gst,
                "discount": discount,
                "total": total,
                "payment": self.payment_combo.get(),
            }

        receipt_text = self.build_receipt_text(sale)

        window = ctk.CTkToplevel(self)
        window.title("Print Invoice")
        window.geometry("1200x750")
        window.grab_set()

        textbox = ctk.CTkTextbox(
            window,
            font=("Courier New", 13),
            wrap="none"
        )
        textbox.pack(fill="both", expand=True, padx=15, pady=15)
        textbox.insert("1.0", receipt_text)
        textbox.configure(state="disabled")

        button_row = ctk.CTkFrame(window, fg_color="transparent")
        button_row.pack(pady=(0, 15))

        ctk.CTkButton(
            button_row,
            text="💾 Save as Text",
            fg_color=colors.SUCCESS,
            hover_color=colors.SUCCESS_HOVER,
            command=lambda: self.save_receipt_to_file(receipt_text, sale["invoice"])
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_row,
            text="🖨 Print",
            fg_color=colors.PRIMARY,
            hover_color=colors.PRIMARY_HOVER,
            command=lambda: self.send_to_printer(receipt_text)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_row,
            text="Close",
            fg_color=colors.SIDEBAR_BUTTON,
            command=window.destroy
        ).pack(side="left", padx=5)

    def build_receipt_text(self, sale):

        company = get_company()

        company_name = (company["company_name"] if company else None) or "BatteryERP Professional"
        company_phone = (company["phone"] if company else "") or ""
        company_address = (company["address"] if company else "") or ""
        company_gstin = (company["gstin"] if company else "") or ""

        subtotal = sale["quantity"] * sale["selling_price"]
        gst_amount = subtotal * sale["gst"] / 100

        width = 42
        line = "-" * width

        lines = []
        lines.append(company_name.center(width))
        if company_address:
            lines.append(company_address.center(width))
        if company_phone:
            lines.append(f"Ph: {company_phone}".center(width))
        if company_gstin:
            lines.append(f"GSTIN: {company_gstin}".center(width))
        lines.append(line)
        lines.append("TAX INVOICE".center(width))
        lines.append(line)
        lines.append(f"Invoice No : {sale['invoice']}")
        lines.append(f"Date       : {sale['date']}  {sale.get('time', '')}")
        lines.append(f"Customer   : {sale['customer']}")
        lines.append(line)
        lines.append(f"{'Item':<18}{'Qty':>6}{'Price':>9}{'Amt':>9}")
        lines.append(line)
        item_amount = sale["quantity"] * sale["selling_price"]
        lines.append(
            f"{sale['product'][:18]:<18}"
            f"{sale['quantity']:>6}"
            f"{sale['selling_price']:>9.2f}"
            f"{item_amount:>9.2f}"
        )
        lines.append(line)
        lines.append(f"{'Subtotal':<33}{subtotal:>9.2f}")
        lines.append(f"{'GST (' + str(sale['gst']) + '%)':<33}{gst_amount:>9.2f}")
        lines.append(f"{'Discount':<33}{sale['discount']:>9.2f}")
        lines.append(line)
        lines.append(f"{'TOTAL':<33}{sale['total']:>9.2f}")
        lines.append(line)
        lines.append(f"Payment Mode: {sale['payment']}")
        lines.append(f"Warranty    : {sale.get('warranty_type', 'Comprehensive')}")
        lines.append(line)
        lines.append("Thank you for your business!".center(width))

        return "\n".join(lines)

    def save_receipt_to_file(self, receipt_text, invoice_no):

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=f"{invoice_no}.txt",
            filetypes=[("Text Files", "*.txt")]
        )

        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(receipt_text)

        messagebox.showinfo("Saved", f"Invoice saved to:\n{path}")

    def send_to_printer(self, receipt_text):
        """
        Sends the receipt to the OS default printer where supported.
        Falls back to informing the user if printing isn't available
        on this platform/setup.
        """
        import tempfile
        import os
        import sys

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".txt",
                delete=False,
                encoding="utf-8"
            ) as tmp:
                tmp.write(receipt_text)
                tmp_path = tmp.name

            if sys.platform.startswith("win"):
                os.startfile(tmp_path, "print")
            elif sys.platform.startswith("darwin"):
                os.system(f'lpr "{tmp_path}"')
            else:
                os.system(f'lpr "{tmp_path}"')

            messagebox.showinfo(
                "Print",
                "Invoice sent to the default printer."
            )

        except Exception:
            messagebox.showwarning(
                "Print Unavailable",
                "No printer was found on this system. "
                "Use 'Save as Text' instead and print it manually."
            )