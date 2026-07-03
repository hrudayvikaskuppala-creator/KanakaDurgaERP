import customtkinter as ctk

from assets.themes import colors


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, current_user=None):
        super().__init__(
            parent,
            width=230,
            corner_radius=0,
            fg_color=colors.SIDEBAR
        )

        self.parent = parent
        self.current_user = current_user
        self.grid_propagate(False)
        self.buttons = {}

        # ------------------------------------------------------------
        # Brand / Logo block
        # ------------------------------------------------------------
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(fill="x", pady=(25, 20), padx=15)

        ctk.CTkLabel(
            brand,
            text="🔋",
            font=(colors.FONT_FAMILY, 30)
        ).pack()

        ctk.CTkLabel(
            brand,
            text="BatteryERP",
            font=(colors.FONT_FAMILY, 19, "bold"),
            text_color=colors.TEXT_ON_PRIMARY
        ).pack()

        ctk.CTkLabel(
            brand,
            text="PROFESSIONAL",
            font=(colors.FONT_FAMILY, 10, "bold"),
            text_color=colors.SIDEBAR_TEXT_MUTED
        ).pack()

        divider = ctk.CTkFrame(self, height=1, fg_color=colors.SIDEBAR_BUTTON)
        divider.pack(fill="x", padx=15, pady=(0, 10))

        # ------------------------------------------------------------
        # Nav Menu
        # ------------------------------------------------------------
        menus = [
            ("home", "🏠  Dashboard", self.parent.show_home),
            ("customers", "👥  Customers", self.parent.show_customers),
            ("products", "📦  Products", self.parent.show_products),
            ("suppliers", "🚚  Suppliers", self.parent.show_suppliers),
            ("purchase", "🛒  Purchase", self.parent.show_purchase),
            ("sales", "🧾  Sales", self.parent.show_sales),
            ("reports", "📊  Reports", self.parent.show_reports),
        ]

        is_admin = bool(current_user) and current_user["role"] == "Admin"

        if is_admin:
            menus.append(("users", "👤  Users", self.parent.show_users))

        menus.append(("settings", "⚙  Settings", self.parent.show_settings))

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12)

        for key, text, command in menus:
            btn = ctk.CTkButton(
                nav_frame,
                text=text,
                anchor="w",
                width=200,
                height=42,
                corner_radius=colors.RADIUS_SM,
                font=colors.FONT_BODY_BOLD,
                fg_color="transparent",
                hover_color=colors.SIDEBAR_BUTTON_HOVER,
                text_color=colors.SIDEBAR_TEXT,
                command=lambda k=key, c=command: self.select(k, c)
            )
            btn.pack(pady=4)
            self.buttons[key] = btn

        # Push footer to bottom
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        divider2 = ctk.CTkFrame(self, height=1, fg_color=colors.SIDEBAR_BUTTON)
        divider2.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkButton(
            self,
            text="🚪  Logout",
            anchor="w",
            width=200,
            height=40,
            corner_radius=colors.RADIUS_SM,
            font=colors.FONT_BODY_BOLD,
            fg_color="transparent",
            hover_color=colors.DANGER,
            text_color=colors.SIDEBAR_TEXT,
            command=lambda: self.parent.logout()
        ).pack(padx=12, pady=(0, 5))

        footer = ctk.CTkLabel(
            self,
            text="v1.0.0",
            font=colors.FONT_SMALL,
            text_color=colors.SIDEBAR_TEXT_MUTED
        )
        footer.pack(pady=10)

        self.set_active("home")

    def select(self, key, command):
        self.set_active(key)
        command()

    def set_active(self, key):
        for btn_key, btn in self.buttons.items():
            if btn_key == key:
                btn.configure(fg_color=colors.SIDEBAR_ACTIVE)
            else:
                btn.configure(fg_color="transparent")
