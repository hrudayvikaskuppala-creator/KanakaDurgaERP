import customtkinter as ctk

from assets.themes import colors
from services.dashboard_service import get_dashboard_stats
from ui.components.watermark import add_watermark


class DashboardHome(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        add_watermark(self)

        stats = get_dashboard_stats()

        title = ctk.CTkLabel(
            self,
            text="Welcome back 👋",
            font=colors.FONT_H1
        )
        title.pack(anchor="w", padx=10, pady=(10, 0))

        subtitle = ctk.CTkLabel(
            self,
            text="Here's what's happening in your shop today.",
            font=colors.FONT_BODY,
            text_color=colors.TEXT_LIGHT
        )
        subtitle.pack(anchor="w", padx=10, pady=(0, 20))

        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.pack(fill="x", padx=10, pady=10)

        for i in range(5):
            cards.grid_columnconfigure(i, weight=1)

        data = [
            ("👥", "Customers", stats["customers"], colors.SECONDARY),
            ("📦", "Products", stats["products"], colors.SUCCESS),
            ("🚚", "Suppliers", stats["suppliers"], colors.INFO),
            ("💰", "Stock Value", f"₹ {stats['stock_value']:,.2f}", colors.PRIMARY),
            ("⚠️", "Low Stock", stats["low_stock"], colors.WARNING if stats["low_stock"] else colors.SUCCESS),
        ]

        for i, (icon, title_text, value, accent) in enumerate(data):
            card = ctk.CTkFrame(
                cards,
                fg_color=colors.CARD,
                corner_radius=colors.RADIUS,
                border_width=0
            )
            card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")

            accent_bar = ctk.CTkFrame(
                card, height=4, corner_radius=0, fg_color=accent
            )
            accent_bar.pack(fill="x", side="top")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=18, pady=16)

            ctk.CTkLabel(
                inner,
                text=icon,
                font=(colors.FONT_FAMILY, 22)
            ).pack(anchor="w")

            ctk.CTkLabel(
                inner,
                text=str(value),
                font=colors.FONT_STAT_VALUE,
                text_color=colors.TEXT
            ).pack(anchor="w", pady=(6, 0))

            ctk.CTkLabel(
                inner,
                text=title_text,
                font=colors.FONT_STAT_LABEL,
                text_color=colors.TEXT_LIGHT
            ).pack(anchor="w")

        # ------------------------------------------------------------
        # Low stock notice banner
        # ------------------------------------------------------------
        if stats["low_stock"]:
            banner = ctk.CTkFrame(
                self,
                fg_color="#FEF3C7",
                corner_radius=colors.RADIUS
            )
            banner.pack(fill="x", padx=10, pady=(10, 0))

            ctk.CTkLabel(
                banner,
                text=(
                    f"⚠️  {stats['low_stock']} product(s) are at or below "
                    "their minimum stock level. Check the Reports page "
                    "for details."
                ),
                font=colors.FONT_BODY_BOLD,
                text_color="#92400E"
            ).pack(padx=15, pady=10, anchor="w")

        # ------------------------------------------------------------
        # Quick tips
        # ------------------------------------------------------------
        tips_card = ctk.CTkFrame(
            self, fg_color=colors.CARD, corner_radius=colors.RADIUS
        )
        tips_card.pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(
            tips_card,
            text="Quick Start",
            font=colors.FONT_H3,
            text_color=colors.PRIMARY
        ).pack(anchor="w", padx=20, pady=(15, 5))

        tips = [
            "Add your Customers and Products before recording a Sale.",
            "Use the Purchase page to restock inventory from Suppliers.",
            "Visit Reports to export Sales, Purchases and Stock as CSV.",
            "Set your company details under Settings so invoices print correctly.",
        ]

        for tip in tips:
            ctk.CTkLabel(
                tips_card,
                text=f"•  {tip}",
                font=colors.FONT_BODY,
                text_color=colors.TEXT_LIGHT,
                anchor="w",
                justify="left"
            ).pack(anchor="w", padx=20, pady=2)

        ctk.CTkLabel(tips_card, text="", height=1).pack(pady=5)
