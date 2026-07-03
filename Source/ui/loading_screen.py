"""
===========================================
 Loading Screen
===========================================
Shown right after a successful login, before the dashboard opens.
Plays an optional devotional/branding image + audio clip supplied by
the shop owner (see assets/splash/README.md) and always falls back
to a clean animated loading screen if those files aren't present, so
the app never breaks because an asset is missing.
"""

import os
import customtkinter as ctk

from assets.themes import colors
from config import APP_NAME
from services import audio_service

SPLASH_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "splash"
)

IMAGE_CANDIDATES = ["splash_image.png", "splash_image.jpg", "splash_image.jpeg"]

DURATION_MS = 3200          # total time the splash stays on screen
PROGRESS_STEP_MS = 40       # how often the progress bar advances


def _find_asset(candidates):
    for name in candidates:
        path = os.path.join(SPLASH_DIR, name)
        if os.path.isfile(path):
            return path
    return None


def show_loading_screen(user, on_complete):
    """
    Displays the loading screen for a short animated duration, then
    calls on_complete() to open the dashboard.
    """
    window = ctk.CTk()
    window.title(APP_NAME)
    window.geometry("560x620")
    window.resizable(False, False)
    window.configure(fg_color=colors.PRIMARY)

    try:
        window.attributes("-topmost", True)
    except Exception:
        pass

    content = ctk.CTkFrame(window, fg_color="transparent")
    content.pack(expand=True)

    image_path = _find_asset(IMAGE_CANDIDATES)

    if image_path:
        try:
            from PIL import Image
            pil_image = Image.open(image_path)
            pil_image.thumbnail((320, 320))
            ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=pil_image.size
            )
            ctk.CTkLabel(content, image=ctk_image, text="").pack(pady=(30, 15))
        except Exception:
            image_path = None

    if not image_path:
        # Clean branded fallback - no external asset required.
        ctk.CTkLabel(
            content,
            text="🔋",
            font=(colors.FONT_FAMILY, 80)
        ).pack(pady=(60, 15))

    full_name = (user["full_name"] if user else None) or "there"

    ctk.CTkLabel(
        content,
        text=f"Welcome, {full_name}",
        font=(colors.FONT_FAMILY, 22, "bold"),
        text_color=colors.TEXT_ON_PRIMARY
    ).pack(pady=(5, 2))

    ctk.CTkLabel(
        content,
        text="Preparing your dashboard...",
        font=colors.FONT_BODY,
        text_color="#DBEAFE"
    ).pack(pady=(0, 25))

    progress = ctk.CTkProgressBar(
        content, width=340, height=10, corner_radius=5,
        progress_color=colors.TEXT_ON_PRIMARY
    )
    progress.pack(pady=10)
    progress.set(0)

    audio_service.play_background_music(loop=True)

    steps = max(1, DURATION_MS // PROGRESS_STEP_MS)
    state = {"step": 0}

    def advance():
        state["step"] += 1
        progress.set(min(1.0, state["step"] / steps))

        if state["step"] >= steps:
            window.destroy()
            on_complete()
        else:
            window.after(PROGRESS_STEP_MS, advance)

    window.after(PROGRESS_STEP_MS, advance)
    window.mainloop()
