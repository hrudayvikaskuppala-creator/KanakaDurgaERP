import customtkinter as ctk
from datetime import datetime

from assets.themes import colors
from config import APP_NAME
from services.campany_service import get_company
from services import audio_service


class Header(ctk.CTkFrame):

    def __init__(self, parent, current_user=None, on_logout=None):
        super().__init__(
            parent,
            height=70,
            corner_radius=0,
            fg_color=colors.HEADER
        )

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        company = get_company()
        display_name = (company["company_name"] if company else None) or APP_NAME

        title_block = ctk.CTkFrame(self, fg_color="transparent")
        title_block.grid(row=0, column=0, padx=25, pady=10, sticky="w")

        ctk.CTkLabel(
            title_block,
            text=display_name,
            font=colors.FONT_H2,
            text_color=colors.PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_block,
            text=datetime.now().strftime("%A, %d %B %Y"),
            font=colors.FONT_SMALL,
            text_color=colors.TEXT_LIGHT
        ).pack(anchor="w")

        # ------------------------------------------------------------
        # User badge
        # ------------------------------------------------------------
        user_block = ctk.CTkFrame(self, fg_color="transparent")
        user_block.grid(row=0, column=1, padx=25, pady=10, sticky="e")

        full_name = (current_user["full_name"] if current_user else None) or "Admin"
        role = (current_user["role"] if current_user else None) or "Administrator"
        initial = full_name.strip()[:1].upper() if full_name.strip() else "A"

        avatar = ctk.CTkLabel(
            user_block,
            text=initial,
            width=36,
            height=36,
            corner_radius=18,
            fg_color=colors.PRIMARY,
            text_color=colors.TEXT_ON_PRIMARY,
            font=colors.FONT_BODY_BOLD
        )
        avatar.pack(side="left", padx=(0, 10))

        name_block = ctk.CTkFrame(user_block, fg_color="transparent")
        name_block.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(
            name_block,
            text=full_name,
            font=colors.FONT_BODY_BOLD,
            text_color=colors.TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            name_block,
            text=role,
            font=colors.FONT_SMALL,
            text_color=colors.TEXT_LIGHT
        ).pack(anchor="w")

        if on_logout:
            ctk.CTkButton(
                user_block,
                text="Logout",
                width=80,
                height=32,
                corner_radius=colors.RADIUS_SM,
                font=colors.FONT_SMALL_BOLD,
                fg_color=colors.DANGER,
                hover_color=colors.DANGER_HOVER,
                command=on_logout
            ).pack(side="left")

        # ------------------------------------------------------------
        # Audio mute/unmute (top-right corner)
        # ------------------------------------------------------------
        self.sound_button = ctk.CTkButton(
            user_block,
            text=self._sound_icon(),
            width=36,
            height=32,
            corner_radius=colors.RADIUS_SM,
            font=(colors.FONT_FAMILY, 16),
            fg_color=colors.SIDEBAR_BUTTON,
            hover_color=colors.SIDEBAR_BUTTON_HOVER,
            command=self.toggle_sound
        )
        self.sound_button.pack(side="left", padx=(10, 0))

    def _sound_icon(self):
        return "🔇" if audio_service.is_muted() else "🔊"

    def toggle_sound(self):
        audio_service.toggle_mute()
        self.sound_button.configure(text=self._sound_icon())
