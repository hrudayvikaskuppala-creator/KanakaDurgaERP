import customtkinter as ctk
from tkinter import messagebox, ttk

from assets.themes import colors

from ui.sidebar import Sidebar
from ui.header import Header
from ui.dashboard_home import DashboardHome

from ui.customer_page import CustomerPage
from ui.product_page import ProductPage
from ui.supplier_page import SupplierPage
from ui.purchase_page import PurchasePage
from ui.sales_page import SalesPage
from ui.reports_page import ReportsPage
from ui.settings_page import SettingsPage
from ui.user_management_page import UserManagementPage

from services.campany_service import get_settings
from services.audit_service import log_action


def apply_treeview_style():
    """
    ttk widgets (used for all the data tables) don't follow
    customtkinter's theming, so we style them once here to match
    the rest of the app.
    """
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=colors.CARD,
        fieldbackground=colors.CARD,
        foreground=colors.TEXT,
        rowheight=32,
        borderwidth=0,
        font=(colors.FONT_FAMILY, 11),
    )
    style.configure(
        "Treeview.Heading",
        background=colors.PRIMARY,
        foreground=colors.TEXT_ON_PRIMARY,
        font=(colors.FONT_FAMILY, 11, "bold"),
        relief="flat",
    )
    style.map(
        "Treeview.Heading",
        background=[("active", colors.PRIMARY_HOVER)],
    )
    style.map(
        "Treeview",
        background=[("selected", colors.SECONDARY)],
        foreground=[("selected", colors.TEXT_ON_PRIMARY)],
    )


class Dashboard(ctk.CTk):

    def __init__(self, current_user=None):
        super().__init__()

        self.current_user = current_user

        self.title("BatteryERP Professional")
        self._apply_responsive_geometry()

        try:
            settings = get_settings()
            saved_theme = settings["theme"] or "light"
            saved_accent = settings["accent_theme"] or "blue"
        except Exception:
            saved_theme = "light"
            saved_accent = "blue"

        ctk.set_appearance_mode(saved_theme)
        ctk.set_default_color_theme("blue")
        colors.apply_accent_theme(saved_accent)

        from services import audio_service
        audio_service.play_background_music(loop=True)

        self._page_name = "home"

        self.build_shell()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.show_home()

    # ------------------------------------------------------------
    # Shell (devotional banner + header + sidebar + content area)
    # ------------------------------------------------------------
    def _apply_responsive_geometry(self):
        """
        Sizes the window relative to the actual screen instead of a
        fixed 1400x800, so it looks right on anything from a small
        laptop panel to a large monitor, and never opens bigger than
        the screen (which used to clip content on smaller displays).
        """
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        # Fit within ~90% of the screen, but don't exceed a sensible
        # "large monitor" cap so it doesn't look stretched-out huge.
        width = min(int(screen_w * 0.92), 1500)
        height = min(int(screen_h * 0.88), 900)

        x = (screen_w - width) // 2
        y = (screen_h - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")

        # A small but usable floor - below this, tables/forms would
        # genuinely start losing important controls.
        self.minsize(1000, 600)

        # On smaller/laptop-class screens, start maximized so nothing
        # feels cramped; larger monitors get the centered window above.
        if screen_w <= 1366 or screen_h <= 768:
            try:
                self.state("zoomed")            # Windows
            except Exception:
                try:
                    self.attributes("-zoomed", True)   # Linux
                except Exception:
                    pass

    def build_shell(self):
        apply_treeview_style()

        self.configure(fg_color=colors.BACKGROUND)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.devotional_banner = ctk.CTkLabel(
            self,
            text="🕉  ఓం నమో వేంకటేశాయ  🕉",
            font=(colors.FONT_FAMILY, 15, "bold"),
            text_color="#FFF7ED",
            fg_color=colors.PRIMARY,
            height=30
        )
        self.devotional_banner.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.header = Header(self, current_user=self.current_user, on_logout=self.logout)
        self.header.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.sidebar = Sidebar(self, current_user=self.current_user)
        self.sidebar.grid(row=2, column=0, sticky="ns")

        self.container = ctk.CTkScrollableFrame(
            self, fg_color=colors.BACKGROUND, scrollbar_button_color=colors.SIDEBAR_BUTTON
        )
        self.container.grid(row=2, column=1, sticky="nsew", padx=15, pady=15)

        self._current_page_widget = None

    def rebuild_shell(self):
        """
        Called after the user changes the accent color in Settings so
        the sidebar/header/banner repaint immediately without needing
        to restart the app. Returns the user to the page they were on.
        """
        for widget in self.winfo_children():
            widget.destroy()

        self.build_shell()

        page_map = {
            "home": self.show_home,
            "customers": self.show_customers,
            "products": self.show_products,
            "suppliers": self.show_suppliers,
            "purchase": self.show_purchase,
            "sales": self.show_sales,
            "reports": self.show_reports,
            "settings": self.show_settings,
            "users": self.show_users,
        }
        page_map.get(self._page_name, self.show_home)()

    def clear_container(self):
        if getattr(self, "_current_page_widget", None) is not None:
            self._current_page_widget.destroy()
            self._current_page_widget = None

    def _show(self, page_class, **kwargs):
        page = page_class(self.container, **kwargs)
        page.pack(fill="both", expand=True)
        self._current_page_widget = page

        # Scroll back to the top whenever a new page is opened.
        try:
            self.container._parent_canvas.yview_moveto(0)
        except Exception:
            pass

        return page

    def show_home(self):
        self._page_name = "home"
        self.clear_container()
        self._show(DashboardHome)

    def show_customers(self):
        self._page_name = "customers"
        self.clear_container()
        self._show(CustomerPage)

    def show_products(self):
        self._page_name = "products"
        self.clear_container()
        self._show(ProductPage)

    def show_suppliers(self):
        self._page_name = "suppliers"
        self.clear_container()
        self._show(SupplierPage)

    def show_purchase(self):
        self._page_name = "purchase"
        self.clear_container()
        self._show(PurchasePage)

    def show_sales(self):
        self._page_name = "sales"
        self.clear_container()
        self._show(SalesPage)

    def show_reports(self):
        self._page_name = "reports"
        self.clear_container()
        self._show(ReportsPage)

    def show_settings(self):
        self._page_name = "settings"
        self.clear_container()
        self._show(SettingsPage, current_user=self.current_user, on_theme_changed=self.rebuild_shell)

    def show_users(self):
        self._page_name = "users"
        self.clear_container()
        self._show(UserManagementPage, current_user=self.current_user)

    def logout(self):
        if not messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            return

        if self.current_user:
            log_action(self.current_user["username"], "Logged out")

        self.destroy()

        from ui.login import open_login
        open_login()

    def on_close(self):
        if self.current_user:
            log_action(self.current_user["username"], "Closed application")
        self.destroy()


def open_dashboard(current_user=None):
    app = Dashboard(current_user=current_user)
    app.mainloop()
