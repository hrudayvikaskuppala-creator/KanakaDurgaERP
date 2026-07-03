"""
===========================================
 Settings Page
===========================================
Lets the shop owner configure their company profile (used on
invoices), the app's appearance / currency preferences, and change
the admin password.
"""

import customtkinter as ctk
from tkinter import messagebox
from services.audio_import_service import import_audio
from services.payment_settings_service import (
    load_payment_settings,
    save_payment_settings
)

from assets.themes import colors
from services.campany_service import (
    get_company,
    save_company,
    get_settings,
    save_settings
)
from models.user import change_password
from ui.components.watermark import add_watermark


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent, current_user=None, on_theme_changed=None):
        super().__init__(parent, fg_color="transparent")

        add_watermark(self)

        self.current_user = current_user
        self.on_theme_changed = on_theme_changed

        title = ctk.CTkLabel(
            self,
            text="Settings",
            font=colors.FONT_H1
        )
        title.pack(anchor="w", padx=10, pady=(10, 0))

        subtitle_text = "Manage your company profile, appearance and account."

        if current_user:
            subtitle_text += f"  •  Logged in as {current_user['full_name']} ({current_user['role']})"

        subtitle = ctk.CTkLabel(
            self,
            text=subtitle_text,
            font=colors.FONT_BODY,
            text_color=colors.TEXT_LIGHT
        )
        subtitle.pack(anchor="w", padx=10, pady=(0, 20))

        self.build_company_section()
        self.build_appearance_section()
        self.build_payment_section()   # <-- New
        self.build_security_section()

        self.load_company()
        self.load_preferences()
        self.load_payment_settings_ui()   # <-- New

    # ------------------------------------------------------------
    # Section: Company Profile
    # ------------------------------------------------------------
    def build_company_section(self):

        card = ctk.CTkFrame(
            self,
            fg_color=colors.CARD,
            corner_radius=colors.RADIUS
        )
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            card,
            text="🏢  Company Profile",
            font=colors.FONT_H3,
            text_color=colors.PRIMARY
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(18, 12))

        card.grid_columnconfigure((1, 3), weight=1)

        # Company name
        ctk.CTkLabel(card, text="Company Name", font=colors.FONT_BODY_BOLD).grid(
            row=1, column=0, padx=20, pady=8, sticky="w"
        )
        self.company_name = ctk.CTkEntry(card, width=280)
        self.company_name.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        # GSTIN
        ctk.CTkLabel(card, text="GSTIN", font=colors.FONT_BODY_BOLD).grid(
            row=1, column=2, padx=10, pady=8, sticky="w"
        )
        self.gstin = ctk.CTkEntry(card, width=280)
        self.gstin.grid(row=1, column=3, padx=20, pady=8, sticky="ew")

        # Phone
        ctk.CTkLabel(card, text="Phone", font=colors.FONT_BODY_BOLD).grid(
            row=2, column=0, padx=20, pady=8, sticky="w"
        )
        self.phone = ctk.CTkEntry(card, width=280)
        self.phone.grid(row=2, column=1, padx=10, pady=8, sticky="ew")

        # Email
        ctk.CTkLabel(card, text="Email", font=colors.FONT_BODY_BOLD).grid(
            row=2, column=2, padx=10, pady=8, sticky="w"
        )
        self.email = ctk.CTkEntry(card, width=280)
        self.email.grid(row=2, column=3, padx=20, pady=8, sticky="ew")

        # Website
        ctk.CTkLabel(card, text="Website", font=colors.FONT_BODY_BOLD).grid(
            row=3, column=0, padx=20, pady=8, sticky="w"
        )
        self.website = ctk.CTkEntry(card, width=280)
        self.website.grid(row=3, column=1, padx=10, pady=8, sticky="ew")

        # Address
        ctk.CTkLabel(card, text="Address", font=colors.FONT_BODY_BOLD).grid(
            row=4, column=0, padx=20, pady=8, sticky="nw"
        )
        self.address = ctk.CTkTextbox(card, width=560, height=70)
        self.address.grid(
            row=4, column=1, columnspan=3, padx=10, pady=8, sticky="ew"
        )

        ctk.CTkButton(
            card,
            text="Save Company Profile",
            font=colors.FONT_BUTTON,
            fg_color=colors.PRIMARY,
            hover_color=colors.PRIMARY_HOVER,
            height=colors.BUTTON_HEIGHT,
            corner_radius=colors.RADIUS_SM,
            command=self.save_company_profile
        ).grid(row=5, column=0, columnspan=4, padx=20, pady=(10, 20), sticky="w")

    # ------------------------------------------------------------
    # Section: Appearance / Preferences
    # ------------------------------------------------------------
    def build_appearance_section(self):

        card = ctk.CTkFrame(
            self,
            fg_color=colors.CARD,
            corner_radius=colors.RADIUS
        )
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            card,
            text="🎨  Appearance & Preferences",
            font=colors.FONT_H3,
            text_color=colors.PRIMARY
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(18, 12))

        ctk.CTkLabel(card, text="Theme", font=colors.FONT_BODY_BOLD).grid(
            row=1, column=0, padx=20, pady=8, sticky="w"
        )
        self.theme_option = ctk.CTkOptionMenu(
            card,
            values=["Light", "Dark", "System"],
            width=200
        )
        self.theme_option.grid(row=1, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(card, text="Currency", font=colors.FONT_BODY_BOLD).grid(
            row=1, column=2, padx=10, pady=8, sticky="w"
        )
        self.currency_option = ctk.CTkOptionMenu(
            card,
            values=["INR", "USD", "EUR", "GBP"],
            width=200
        )
        self.currency_option.grid(row=1, column=3, padx=20, pady=8, sticky="w")

        ctk.CTkLabel(card, text="Accent Color", font=colors.FONT_BODY_BOLD).grid(
            row=2, column=0, padx=20, pady=8, sticky="w"
        )
        self._accent_labels = list(colors.THEME_LABELS.values())
        self._accent_keys_by_label = {v: k for k, v in colors.THEME_LABELS.items()}
        self.accent_option = ctk.CTkOptionMenu(
            card,
            values=self._accent_labels,
            width=200
        )
        self.accent_option.grid(row=2, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(
            card,
            text="Choose a color palette for the sidebar, buttons and\naccents across the whole app.",
            font=colors.FONT_SMALL, text_color=colors.TEXT_LIGHT, justify="left"
        ).grid(row=2, column=2, columnspan=2, padx=10, pady=8, sticky="w")

        ctk.CTkButton(
            card,
            text="Save Preferences",
            font=colors.FONT_BUTTON,
            fg_color=colors.SECONDARY,
            hover_color=colors.SECONDARY_HOVER,
            height=colors.BUTTON_HEIGHT,
            corner_radius=colors.RADIUS_SM,
            command=self.save_preferences
        ).grid(row=3, column=0, columnspan=4, padx=20, pady=(10, 20), sticky="w")
        
        ctk.CTkButton(
            card,
            text="🎵 Import Audio",
            font=colors.FONT_BUTTON,
            fg_color=colors.PRIMARY,
            hover_color=colors.PRIMARY_HOVER,
            height=colors.BUTTON_HEIGHT,
            corner_radius=colors.RADIUS_SM,
            command=import_audio
        ).grid(
            row=4,
            column=0,
            padx=20,
            pady=(5,10),
            sticky="w"
)
        
    # ------------------------------------------------------------
    # Section: Payment Integration
    # ------------------------------------------------------------
    def build_payment_section(self):

        card = ctk.CTkFrame(
            self,
            fg_color=colors.CARD,
            corner_radius=colors.RADIUS
        )
        card.pack(fill="x", padx=10, pady=10)

        card.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(
            card,
            text="💳 Payment Integration",
            font=colors.FONT_H3,
            text_color=colors.PRIMARY
        ).grid(
            row=0,
            column=0,
            columnspan=4,
            padx=20,
            pady=(18, 12),
            sticky="w"
        )

        ctk.CTkLabel(
            card,
            text="Payment Provider",
            font=colors.FONT_BODY_BOLD
        ).grid(row=1, column=0, padx=20, pady=8, sticky="w")

        self.provider_option = ctk.CTkOptionMenu(
            card,
            values=[
                "Manual Payment",
                "UPI QR",
                "Razorpay",
                "PhonePe",
                "Paytm",
                "Cashfree",
                "Pine Labs",
                "HDFC SmartHub",
                "ICICI POS",
                "Axis POS",
                "Worldline",
                "MSwipe",
                "Custom"
            ],
            width=260
        )

        self.provider_option.grid(
            row=1,
            column=1,
            padx=10,
            pady=8,
            sticky="w"
        )

        ctk.CTkLabel(
            card,
            text="Merchant ID",
            font=colors.FONT_BODY_BOLD
        ).grid(row=2, column=0, padx=20, pady=8, sticky="w")

        self.merchant_id = ctk.CTkEntry(card, width=260)
        self.merchant_id.grid(
            row=2,
            column=1,
            padx=10,
            pady=8,
            sticky="ew"
        )

        ctk.CTkLabel(
            card,
            text="Terminal ID",
            font=colors.FONT_BODY_BOLD
        ).grid(row=2, column=2, padx=10, pady=8, sticky="w")

        self.terminal_id = ctk.CTkEntry(card, width=260)
        self.terminal_id.grid(
            row=2,
            column=3,
            padx=20,
            pady=8,
            sticky="ew"
        )

        ctk.CTkLabel(
            card,
            text="UPI ID",
            font=colors.FONT_BODY_BOLD
        ).grid(row=3, column=0, padx=20, pady=8, sticky="w")

        self.upi_id = ctk.CTkEntry(card, width=260)
        self.upi_id.grid(
            row=3,
            column=1,
            padx=10,
            pady=8,
            sticky="ew"
        )

        ctk.CTkLabel(
            card,
            text="API Key",
            font=colors.FONT_BODY_BOLD
        ).grid(row=3, column=2, padx=10, pady=8, sticky="w")

        self.api_key = ctk.CTkEntry(card, width=260, show="*")
        self.api_key.grid(
            row=3,
            column=3,
            padx=20,
            pady=8,
            sticky="ew"
        )

        self.auto_print = ctk.CTkCheckBox(
            card,
            text="Automatically Print Invoice"
        )

        self.auto_print.grid(
            row=4,
            column=0,
            padx=20,
            pady=8,
            sticky="w"
        )

        self.auto_whatsapp = ctk.CTkCheckBox(
            card,
            text="Automatically Send WhatsApp Invoice"
        )

        self.auto_whatsapp.grid(
            row=4,
            column=1,
            padx=20,
            pady=8,
            sticky="w"
        )

        ctk.CTkButton(
            card,
            text="💾 Save Payment Settings",
            font=colors.FONT_BUTTON,
            fg_color=colors.PRIMARY,
            hover_color=colors.PRIMARY_HOVER,
            command=self.save_payment_settings_ui
        ).grid(
            row=5,
            column=0,
            padx=20,
            pady=(15, 20),
            sticky="w"
        )

        ctk.CTkButton(
            card,
            text="🔌 Test Connection",
            font=colors.FONT_BUTTON,
            fg_color=colors.SECONDARY,
            hover_color=colors.SECONDARY_HOVER,
            command=self.test_payment_connection
        ).grid(
            row=5,
            column=1,
            padx=10,
            pady=(15, 20),
            sticky="w"
        )

        ctk.CTkButton(
            card,
            text="↺ Reset",
            font=colors.FONT_BUTTON,
            fg_color=colors.DANGER,
            hover_color=colors.DANGER_HOVER,
            command=self.reset_payment_settings
        ).grid(
            row=5,
            column=2,
            padx=10,
            pady=(15, 20),
            sticky="w"
        )

    # ------------------------------------------------------------
    # Section: Security
    # ------------------------------------------------------------
    def build_security_section(self):

        card = ctk.CTkFrame(
            self,
            fg_color=colors.CARD,
            corner_radius=colors.RADIUS
        )
        card.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            card,
            text="🔒  Change Password",
            font=colors.FONT_H3,
            text_color=colors.PRIMARY
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(18, 12))

        ctk.CTkLabel(card, text="Current Password", font=colors.FONT_BODY_BOLD).grid(
            row=1, column=0, padx=20, pady=8, sticky="w"
        )
        self.current_password = ctk.CTkEntry(card, width=220, show="*")
        self.current_password.grid(row=1, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(card, text="New Password", font=colors.FONT_BODY_BOLD).grid(
            row=1, column=2, padx=10, pady=8, sticky="w"
        )
        self.new_password = ctk.CTkEntry(card, width=220, show="*")
        self.new_password.grid(row=1, column=3, padx=20, pady=8, sticky="w")

        ctk.CTkButton(
            card,
            text="Update Password",
            font=colors.FONT_BUTTON,
            fg_color=colors.DANGER,
            hover_color=colors.DANGER_HOVER,
            height=colors.BUTTON_HEIGHT,
            corner_radius=colors.RADIUS_SM,
            command=self.update_password
        ).grid(row=2, column=0, columnspan=4, padx=20, pady=(10, 20), sticky="w")

    # ------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------
    def load_company(self):
        company = get_company()

        if not company:
            return

        self.company_name.insert(0, company["company_name"] or "")
        self.gstin.insert(0, company["gstin"] or "")
        self.phone.insert(0, company["phone"] or "")
        self.email.insert(0, company["email"] or "")
        self.website.insert(0, company["website"] or "")
        self.address.insert("1.0", company["address"] or "")

    def load_preferences(self):
        settings = get_settings()

        theme = (settings["theme"] or "light").capitalize()
        currency = settings["currency"] or "INR"
        accent_key = settings["accent_theme"] or "blue"

        self.theme_option.set(theme)
        self.currency_option.set(currency)
        self.accent_option.set(colors.THEME_LABELS.get(accent_key, "Classic Blue"))

    # ------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------
    def save_company_profile(self):

        name = self.company_name.get().strip()

        if not name:
            messagebox.showwarning(
                "Validation",
                "Company Name is required."
            )
            return

        save_company(
            name,
            self.gstin.get().strip(),
            self.phone.get().strip(),
            self.email.get().strip(),
            self.address.get("1.0", "end").strip(),
            self.website.get().strip()
        )

        messagebox.showinfo(
            "Success",
            "Company profile saved successfully."
        )

    def save_preferences(self):

        theme = self.theme_option.get().lower()
        currency = self.currency_option.get()
        accent_label = self.accent_option.get()
        accent_key = self._accent_keys_by_label.get(accent_label, "blue")

        save_settings(theme, currency, accent_key)

        ctk.set_appearance_mode(theme)
        colors.apply_accent_theme(accent_key)

        if self.on_theme_changed:
            self.on_theme_changed()

        messagebox.showinfo(
            "Success",
            "Preferences saved successfully. The new accent color is now applied."
        )

    def load_payment_settings_ui(self):

        settings = load_payment_settings()

        self.provider_option.set(
            settings.get("provider", "Manual Payment")
        )

        self.merchant_id.insert(
            0,
            settings.get("merchant_id", "")
        )

        self.terminal_id.insert(
            0,
            settings.get("terminal_id", "")
        )

        self.upi_id.insert(
            0,
            settings.get("upi_id", "")
        )

        self.api_key.insert(
            0,
            settings.get("api_key", "")
        )

        if settings.get("auto_print", True):
            self.auto_print.select()

        if settings.get("auto_whatsapp", True):
            self.auto_whatsapp.select()
            
    def save_payment_settings_ui(self):

        settings = {

            "provider": self.provider_option.get(),

            "merchant_id": self.merchant_id.get(),

            "terminal_id": self.terminal_id.get(),

            "upi_id": self.upi_id.get(),

            "api_key": self.api_key.get(),

            "auto_print": bool(self.auto_print.get()),

            "auto_whatsapp": bool(self.auto_whatsapp.get())

        }

        save_payment_settings(settings)

        messagebox.showinfo(
            "Success",
            "Payment settings saved successfully."
        )

    def test_payment_connection(self):

        provider = self.provider_option.get()

        if provider == "Manual Payment":
            messagebox.showinfo(
                "Connection Test",
                "Manual Payment mode does not require a connection."
            )
            return

        if provider == "UPI QR":
            if not self.upi_id.get().strip():
                messagebox.showwarning(
                    "Validation",
                    "Please enter a valid UPI ID."
                )
                return

            messagebox.showinfo(
                "Success",
                "UPI configuration looks valid."
            )
            return

        if not self.merchant_id.get().strip():
            messagebox.showwarning(
                "Validation",
                "Merchant ID is required."
            )
            return

        if not self.api_key.get().strip():
            messagebox.showwarning(
                "Validation",
                "API Key is required."
            )
            return

        messagebox.showinfo(
            "Connection Successful",
            f"{provider} configuration looks valid.\n\n"
            "Live API verification will be available after integrating the provider SDK/API."
        )

    def reset_payment_settings(self):

        self.provider_option.set("Manual Payment")

        self.merchant_id.delete(0, "end")
        self.terminal_id.delete(0, "end")
        self.upi_id.delete(0, "end")
        self.api_key.delete(0, "end")

        self.auto_print.select()
        self.auto_whatsapp.select()

        messagebox.showinfo(
            "Reset",
            "Payment settings have been reset."
        )

    def update_password(self):

        current = self.current_password.get()
        new = self.new_password.get()

        if not current or not new:
            messagebox.showwarning(
                "Validation",
                "Please fill both password fields."
            )
            return

        if len(new) < 6:
            messagebox.showwarning(
                "Validation",
                "New password must be at least 6 characters."
            )
            return

        username = self.current_user["username"] if self.current_user else "admin"

        success = change_password(username, current, new)

        if success:
            messagebox.showinfo(
                "Success",
                "Password updated successfully."
            )
            self.current_password.delete(0, "end")
            self.new_password.delete(0, "end")
        else:
            messagebox.showerror(
                "Error",
                "Current password is incorrect."
            )
