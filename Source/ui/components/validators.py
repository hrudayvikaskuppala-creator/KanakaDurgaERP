"""
===========================================
 Shared Input Validation Helpers
===========================================
Two layers, used together everywhere in the app:

1. Live keystroke filters (attach_* functions) - stop invalid
   characters from ever being typed, using Tk's built-in validation
   hook (`validatecommand`). E.g. a mobile field simply can't accept
   a letter.

2. Save-time checks (validate_* functions) - return (True, "") or
   (False, "friendly message") so a page can show a clear warning
   with messagebox before writing to the database.

Keeping both layers means the UI feels responsive (bad keys are
rejected instantly) while still catching things like "field left
empty" or "mobile number too short" before saving.
"""

import re
from tkinter import messagebox


# ------------------------------------------------------------------
# Layer 1 - live keystroke filters
# ------------------------------------------------------------------
def _register(widget, callback):
    vcmd = (widget.register(callback), "%P")
    widget.configure(validate="key", validatecommand=vcmd)


def attach_digits_only(entry, max_len=None):
    """Only 0-9. Use for mobile numbers, invoice numbers, whole counts."""
    def check(value):
        if value == "":
            return True
        if not value.isdigit():
            return False
        if max_len and len(value) > max_len:
            return False
        return True

    _register(entry, check)


def attach_decimal_only(entry, max_digits_before_point=8):
    """Digits with at most one decimal point. Use for price, GST, discount, qty."""
    def check(value):
        if value == "":
            return True
        if value == ".":
            return True
        if not re.fullmatch(r"\d{0,%d}(\.\d{0,2})?" % max_digits_before_point, value):
            return False
        return True

    _register(entry, check)


def attach_text_only(entry, allow_numbers=False):
    """
    Letters, spaces and a small set of punctuation used in real names
    / addresses (. , - & ' / #). Use for supplier/customer/brand/model
    names and free-text address fields.
    """
    pattern = (
    r"[A-Za-z\s\.,\-&'/#()_+/]*"
    if not allow_numbers
    else r"[A-Za-z0-9\s\.,\-&'/#()_+/]*"
)

    def check(value):
        if value == "":
            return True
        return re.fullmatch(pattern, value) is not None

    _register(entry, check)


def attach_alnum(entry):
    """Letters + numbers + a few separators. Use for invoice/model codes."""
    def check(value):
        if value == "":
            return True
        return re.fullmatch(r"[A-Za-z0-9\-\/_]*", value) is not None

    _register(entry, check)


# ------------------------------------------------------------------
# Layer 2 - save-time validation
# ------------------------------------------------------------------
def validate_required(value, field_name):
    if not value or not value.strip():
        return False, f"{field_name} is required."
    return True, ""


def validate_mobile(value, required=True):
    value = (value or "").strip()
    if not value:
        return (False, "Mobile number is required.") if required else (True, "")
    if not value.isdigit():
        return False, "Mobile number must contain digits only."
    if len(value) != 10:
        return False, "Mobile number must be exactly 10 digits."
    return True, ""


def validate_email(value, required=False):
    value = (value or "").strip()
    if not value:
        return (False, "Email is required.") if required else (True, "")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value):
        return False, "Please enter a valid email address."
    return True, ""


def validate_name(value, field_name, required=True):
    value = (value or "").strip()
    if not value:
        return (False, f"{field_name} is required.") if required else (True, "")
    if not re.fullmatch(r"[A-Za-z0-9\s\.,\-&'/#()_]+", value):
        return False, f"{field_name} can only contain letters and basic punctuation."
    return True, ""


def validate_positive_number(value, field_name, allow_zero=True, required=True):
    value = (value or "").strip()
    if not value:
        return (False, f"{field_name} is required.") if required else (True, "")
    try:
        number = float(value)
    except ValueError:
        return False, f"{field_name} must be a valid number."
    if allow_zero and number < 0:
        return False, f"{field_name} cannot be negative."
    if not allow_zero and number <= 0:
        return False, f"{field_name} must be greater than zero."
    return True, ""


def validate_gst(value, field_name="GST %"):
    value = (value or "").strip()
    if not value:
        return True, ""  # GST defaults to 0
    ok, msg = validate_positive_number(value, field_name)
    if not ok:
        return ok, msg
    if float(value) > 100:
        return False, f"{field_name} cannot be more than 100."
    return True, ""


def show_validation_error(message):
    messagebox.showwarning("Validation", message)


def run_checks(*results):
    """
    Pass any number of (ok, message) tuples. Returns True if all
    passed; otherwise shows the first failure and returns False.
    Usage:
        if not run_checks(
            validate_name(name, "Supplier Name"),
            validate_mobile(mobile),
        ):
            return
    """
    for ok, message in results:
        if not ok:
            show_validation_error(message)
            return False
    return True
