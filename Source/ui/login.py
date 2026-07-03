import customtkinter as ctk
from tkinter import messagebox

from assets.themes import colors
from config import APP_NAME, VERSION
from models.user import login
from ui.dashboard import open_dashboard
from ui.loading_screen import show_loading_screen
from services.audit_service import log_action
from ui.components.watermark import add_watermark


def open_login():

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    try:
        from services.campany_service import get_settings
        colors.apply_accent_theme(get_settings()["accent_theme"] or "blue")
    except Exception:
        pass

    app = ctk.CTk()
    app.title(APP_NAME)
    screen_w = app.winfo_screenwidth()
    screen_h = app.winfo_screenheight()
    width = min(int(screen_w * 0.55), 980)
    height = min(int(screen_h * 0.75), 650)
    width = max(width, 760)   # never smaller than this, or the brand panel/form clip
    height = max(height, 560)
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    app.geometry(f"{width}x{height}+{x}+{y}")
    app.minsize(760, 560)
    app.resizable(True, True)
    app.configure(fg_color=colors.BACKGROUND)

    app.grid_columnconfigure(0, weight=1)
    app.grid_columnconfigure(1, weight=1)
    app.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(
        app,
        text="🕉  ఓం నమో వేంకటేశాయ  🕉",
        font=(colors.FONT_FAMILY, 15, "bold"),
        text_color="#FFF7ED",
        fg_color=colors.PRIMARY,
        height=30
    ).grid(row=0, column=0, columnspan=2, sticky="ew")

    # ===========================
    # Left Brand Panel
    # ===========================
    brand_panel = ctk.CTkFrame(
        app, corner_radius=0, fg_color=colors.PRIMARY
    )
    brand_panel.grid(row=1, column=0, sticky="nsew")

    ctk.CTkLabel(
        brand_panel,
        text="🔋",
        font=(colors.FONT_FAMILY, 64)
    ).pack(pady=(150, 10))

    ctk.CTkLabel(
        brand_panel,
        text=APP_NAME,
        font=(colors.FONT_FAMILY, 26, "bold"),
        text_color=colors.TEXT_ON_PRIMARY
    ).pack()

    ctk.CTkLabel(
        brand_panel,
        text="Complete Battery Shop Management",
        font=colors.FONT_BODY,
        text_color="#DBEAFE"
    ).pack(pady=(5, 0))

    # ===========================
    # Right Login Panel
    # ===========================
    form_panel = ctk.CTkFrame(app, corner_radius=0, fg_color=colors.BACKGROUND)
    form_panel.grid(row=1, column=1, sticky="nsew")

    add_watermark(form_panel, variant="bg", size=(280, 480), relx=0.9, rely=0.5)

    form_card = ctk.CTkFrame(
        form_panel,
        width=340,
        fg_color="transparent"
    )
    form_card.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(
        form_card,
        text="Welcome Back",
        font=colors.FONT_H1,
        text_color=colors.TEXT
    ).pack(pady=(0, 5))

    ctk.CTkLabel(
        form_card,
        text="Sign in to continue to your dashboard",
        font=colors.FONT_BODY,
        text_color=colors.TEXT_LIGHT
    ).pack(pady=(0, 30))

    # ===========================
    # Username
    # ===========================

    username_entry = ctk.CTkEntry(
        form_card,
        width=320,
        height=colors.BUTTON_HEIGHT,
        corner_radius=colors.RADIUS_SM,
        placeholder_text="Username"
    )
    username_entry.pack(pady=10)

    # ===========================
    # Password
    # ===========================

    password_entry = ctk.CTkEntry(
        form_card,
        width=320,
        height=colors.BUTTON_HEIGHT,
        corner_radius=colors.RADIUS_SM,
        placeholder_text="Password",
        show="*"
    )
    password_entry.pack(pady=10)
    password_entry.bind("<Return>", lambda e: authenticate())

    # ===========================
    # Show Password
    # ===========================

    def toggle_password():

        if password_entry.cget("show") == "*":
            password_entry.configure(show="")
        else:
            password_entry.configure(show="*")

    show_password = ctk.CTkCheckBox(
        form_card,
        text="Show Password",
        font=colors.FONT_SMALL,
        command=toggle_password
    )
    show_password.pack(pady=(5, 0), anchor="w")

    # ===========================
    # Login
    # ===========================

    def authenticate():

        username = username_entry.get().strip()
        password = password_entry.get()

        if username == "" or password == "":
            messagebox.showwarning(
                "Validation",
                "Please enter Username and Password."
            )
            return

        user = login(username, password)

        if user:

            if user["status"] == 0:
                messagebox.showerror(
                    "Account Disabled",
                    "This account has been deactivated. Please contact "
                    "your administrator."
                )
                return

            log_action(user["username"], "Logged in")

            app.destroy()
            show_loading_screen(user, lambda: open_dashboard(user))

        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )

    ctk.CTkButton(
        form_card,
        text="Login",
        width=320,
        height=colors.BUTTON_HEIGHT,
        corner_radius=colors.RADIUS_SM,
        font=colors.FONT_BUTTON,
        fg_color=colors.PRIMARY,
        hover_color=colors.PRIMARY_HOVER,
        command=authenticate
    ).pack(pady=25)

    ctk.CTkLabel(
        form_card,
        text="Default: admin / admin123",
        font=colors.FONT_SMALL,
        text_color=colors.TEXT_MUTED
    ).pack()

    ctk.CTkLabel(
        app,
        text=f"Version {VERSION}",
        font=colors.FONT_SMALL,
        text_color=colors.TEXT_MUTED
    ).place(relx=0.5, rely=0.98, anchor="s")

    app.mainloop()
