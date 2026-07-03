"""
===========================================
 BatteryERP Professional - Theme Palette
===========================================
Central place for every color / font used across the UI so the whole
app stays visually consistent and can be re-themed from one file.
"""

# ------------------------------------------------------------------
# Brand Colors
# ------------------------------------------------------------------
PRIMARY = "#1E3A8A"          # deep blue - brand
PRIMARY_HOVER = "#16306E"
SECONDARY = "#2563EB"        # bright blue - accents / links
SECONDARY_HOVER = "#1D4ED8"

SUCCESS = "#16A34A"
SUCCESS_HOVER = "#128038"
WARNING = "#F59E0B"
WARNING_HOVER = "#D9840A"
DANGER = "#DC2626"
DANGER_HOVER = "#B91C1C"
INFO = "#0891B2"
INFO_HOVER = "#0E7490"

# ------------------------------------------------------------------
# Surfaces
# ------------------------------------------------------------------
BACKGROUND = "#F3F4F6"
BACKGROUND_DARK = "#0F172A"

CARD = "#FFFFFF"
CARD_DARK = "#1E293B"

BORDER = "#E5E7EB"

# ------------------------------------------------------------------
# Text
# ------------------------------------------------------------------
TEXT = "#111827"
TEXT_LIGHT = "#6B7280"
TEXT_MUTED = "#9CA3AF"
TEXT_ON_PRIMARY = "#FFFFFF"

# ------------------------------------------------------------------
# Sidebar / Header
# ------------------------------------------------------------------
SIDEBAR = "#111827"
SIDEBAR_BUTTON = "#1F2937"
SIDEBAR_BUTTON_HOVER = "#2563EB"
SIDEBAR_ACTIVE = "#2563EB"
SIDEBAR_TEXT = "#E5E7EB"
SIDEBAR_TEXT_MUTED = "#9CA3AF"

HEADER = "#FFFFFF"
HEADER_BORDER = "#E5E7EB"

# ------------------------------------------------------------------
# Stat Card Accents (Dashboard)
# ------------------------------------------------------------------
CARD_ACCENTS = [SECONDARY, SUCCESS, WARNING, INFO, DANGER]

# ------------------------------------------------------------------
# Fonts
# ------------------------------------------------------------------
FONT_FAMILY = "Segoe UI"

FONT_H1 = (FONT_FAMILY, 28, "bold")
FONT_H2 = (FONT_FAMILY, 22, "bold")
FONT_H3 = (FONT_FAMILY, 18, "bold")
FONT_BODY = (FONT_FAMILY, 14)
FONT_BODY_BOLD = (FONT_FAMILY, 14, "bold")
FONT_SMALL = (FONT_FAMILY, 12)
FONT_SMALL_BOLD = (FONT_FAMILY, 12, "bold")
FONT_BUTTON = (FONT_FAMILY, 14, "bold")
FONT_STAT_VALUE = (FONT_FAMILY, 26, "bold")
FONT_STAT_LABEL = (FONT_FAMILY, 13, "bold")

# ------------------------------------------------------------------
# Common Sizes
# ------------------------------------------------------------------
RADIUS = 10
RADIUS_SM = 6
BUTTON_HEIGHT = 38

# ------------------------------------------------------------------
# Accent Color Presets (Settings -> Appearance)
# ------------------------------------------------------------------
# Each preset re-tints the brand/sidebar colors. Fonts, surfaces and
# status colors (success/warning/danger) stay the same across all of
# them so the app never looks broken - only the "brand" accent shifts.
THEME_PRESETS = {
    "blue": {
        "PRIMARY": "#1E3A8A", "PRIMARY_HOVER": "#16306E",
        "SECONDARY": "#2563EB", "SECONDARY_HOVER": "#1D4ED8",
        "SIDEBAR": "#111827", "SIDEBAR_BUTTON": "#1F2937",
        "SIDEBAR_BUTTON_HOVER": "#2563EB", "SIDEBAR_ACTIVE": "#2563EB",
    },
    "royal_purple": {
        "PRIMARY": "#5B21B6", "PRIMARY_HOVER": "#4C1D95",
        "SECONDARY": "#7C3AED", "SECONDARY_HOVER": "#6D28D9",
        "SIDEBAR": "#1E1B2E", "SIDEBAR_BUTTON": "#2E2A45",
        "SIDEBAR_BUTTON_HOVER": "#7C3AED", "SIDEBAR_ACTIVE": "#7C3AED",
    },
    "emerald_green": {
        "PRIMARY": "#065F46", "PRIMARY_HOVER": "#064E3B",
        "SECONDARY": "#10B981", "SECONDARY_HOVER": "#059669",
        "SIDEBAR": "#0F1F1A", "SIDEBAR_BUTTON": "#1C332B",
        "SIDEBAR_BUTTON_HOVER": "#10B981", "SIDEBAR_ACTIVE": "#10B981",
    },
    "crimson_maroon": {
        "PRIMARY": "#7F1D1D", "PRIMARY_HOVER": "#6B1717",
        "SECONDARY": "#B91C1C", "SECONDARY_HOVER": "#991B1B",
        "SIDEBAR": "#1F1213", "SIDEBAR_BUTTON": "#331C1D",
        "SIDEBAR_BUTTON_HOVER": "#B91C1C", "SIDEBAR_ACTIVE": "#B91C1C",
    },
    "teal": {
        "PRIMARY": "#0F766E", "PRIMARY_HOVER": "#0D5F58",
        "SECONDARY": "#14B8A6", "SECONDARY_HOVER": "#0D9488",
        "SIDEBAR": "#0D1F1E", "SIDEBAR_BUTTON": "#1A3230",
        "SIDEBAR_BUTTON_HOVER": "#14B8A6", "SIDEBAR_ACTIVE": "#14B8A6",
    },
    "sunset_orange": {
        "PRIMARY": "#9A3412", "PRIMARY_HOVER": "#7C2D12",
        "SECONDARY": "#EA580C", "SECONDARY_HOVER": "#C2410C",
        "SIDEBAR": "#231712", "SIDEBAR_BUTTON": "#3A2419",
        "SIDEBAR_BUTTON_HOVER": "#EA580C", "SIDEBAR_ACTIVE": "#EA580C",
    },
    "slate_navy": {
        "PRIMARY": "#1E293B", "PRIMARY_HOVER": "#0F172A",
        "SECONDARY": "#334155", "SECONDARY_HOVER": "#1E293B",
        "SIDEBAR": "#020617", "SIDEBAR_BUTTON": "#0F172A",
        "SIDEBAR_BUTTON_HOVER": "#334155", "SIDEBAR_ACTIVE": "#334155",
    },
}

THEME_LABELS = {
    "blue": "Classic Blue",
    "royal_purple": "Royal Purple",
    "emerald_green": "Emerald Green",
    "crimson_maroon": "Crimson Maroon",
    "teal": "Teal",
    "sunset_orange": "Sunset Orange",
    "slate_navy": "Slate Navy",
}


def apply_accent_theme(name):
    """
    Re-tints the module's brand/sidebar colors in place. Called once
    at app startup (from the saved setting) and again whenever the
    user saves a new choice on the Settings page. Any page/widget
    built *after* this call picks up the new colors automatically
    since they all read `colors.PRIMARY` etc. as module attributes.
    Safe no-op for an unknown name (keeps current colors).
    """
    preset = THEME_PRESETS.get(name)
    if not preset:
        return

    module = globals()
    for key, value in preset.items():
        module[key] = value

    # CARD_ACCENTS is derived from SECONDARY - keep it in sync too.
    module["CARD_ACCENTS"] = [SECONDARY, SUCCESS, WARNING, INFO, DANGER]
