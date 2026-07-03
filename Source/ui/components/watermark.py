"""
===========================================
 Page Watermark Helper
===========================================
Places a subtle, low-opacity devotional image on the right side of a
page as background branding.

Tkinter/CTk widgets don't support true alpha compositing (a widget's
background is a solid color, not a see-through layer), so instead of
trying to render transparency at draw time, the watermark images are
*pre-blended* once (see assets/branding/) at ~7-8% opacity against
the app's actual background/card colors. That file is then placed
with `.place()` in the right-hand margin of a page and lowered in the
stacking order, so it sits quietly behind/beside form fields and
tables without ever covering text or reducing readability.

Usage (call once, right after `super().__init__(...)` in a page):

    from ui.components.watermark import add_watermark
    add_watermark(self)
"""

import os
import customtkinter as ctk
from PIL import Image

_ASSET_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "branding"
)

_CACHE = {}


def _load_image(variant, size):
    key = (variant, size)
    if key in _CACHE:
        return _CACHE[key]

    filename = "watermark_card.png" if variant == "card" else "watermark_bg.png"
    path = os.path.join(_ASSET_DIR, filename)

    if not os.path.isfile(path):
        return None

    try:
        pil_image = Image.open(path)
        pil_image.thumbnail(size)
        image = ctk.CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=pil_image.size
        )
        _CACHE[key] = image
        return image
    except Exception:
        return None


def add_watermark(page, variant="bg", size=(300, 520), relx=0.985, rely=0.55):
    """
    Adds the watermark to a CTk frame/page. Safe no-op if the asset
    is missing so it can never break a page from loading.

    variant: "bg" for pages on the plain background, "card" for
    pages that are mostly one big white card (keeps contrast subtle
    either way).
    """
    try:
        image = _load_image(variant, size)
        if image is None:
            return None

        label = ctk.CTkLabel(page, image=image, text="")
        label.place(relx=relx, rely=rely, anchor="e")
        label.lower()  # sit behind anything packed/gridded on top
        return label
    except Exception:
        # Branding is decorative only - never let it break a page.
        return None
