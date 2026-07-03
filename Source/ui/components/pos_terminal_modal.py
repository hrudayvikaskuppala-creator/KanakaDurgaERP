"""
===========================================
 POS Terminal Modal
===========================================
Shown from the Sales page whenever the payment mode needs a POS
terminal (UPI / Credit Card / Debit Card / QR Code). It calls the
active POS provider (see services/pos/manager.py) to process the
charge, and reports back via callbacks - the Sales page decides what
"success" and "failure" actually do (save the sale, print, show an
error, offer retry, etc.), this modal only owns the terminal UI.

Since no real terminal is wired in yet, the active provider is a
simulator: after a short "connecting" animation, it shows clearly
-labeled test buttons so the full approve/decline/cancel path can be
exercised today. Swapping in a real POS SDK later (see
services/pos/base_provider.py) removes the need for those buttons -
the real provider would report its own outcome instead.
"""

import customtkinter as ctk

from assets.themes import colors
from services.pos.manager import get_active_provider


def open_pos_terminal(parent, amount, payment_mode, invoice_no, on_success, on_failure):
    modal = ctk.CTkToplevel(parent)
    modal.title("POS Payment")
    modal.geometry("440x420")
    modal.resizable(False, False)
    modal.grab_set()
    modal.transient(parent.winfo_toplevel())
    modal.configure(fg_color=colors.BACKGROUND)

    ctk.CTkLabel(
        modal, text="💳 POS Payment", font=colors.FONT_H2, text_color=colors.PRIMARY
    ).pack(pady=(20, 4))

    ctk.CTkLabel(
        modal, text=f"₹ {amount:,.2f}", font=(colors.FONT_FAMILY, 30, "bold"),
        text_color=colors.TEXT
    ).pack(pady=(0, 2))

    ctk.CTkLabel(
        modal, text=f"{payment_mode}  •  Invoice {invoice_no}",
        font=colors.FONT_SMALL, text_color=colors.TEXT_LIGHT
    ).pack(pady=(0, 20))

    status_label = ctk.CTkLabel(
        modal, text="Connecting to POS terminal...", font=colors.FONT_BODY_BOLD,
        text_color=colors.INFO
    )
    status_label.pack(pady=(0, 10))

    progress = ctk.CTkProgressBar(modal, width=320, mode="indeterminate")
    progress.pack(pady=(0, 20))
    progress.start()

    action_frame = ctk.CTkFrame(modal, fg_color="transparent")

    provider = get_active_provider()

    def run_charge(decision):
        progress.stop()
        status_label.configure(text="Processing payment...", text_color=colors.INFO)
        modal.update_idletasks()

        result = provider.charge(
            amount, payment_mode, invoice_no,
            simulate_decision=lambda: decision
        )

        modal.destroy()

        if result.success:
            on_success(result, provider.provider_name)
        else:
            on_failure(result, provider.provider_name)

    def reveal_test_controls():
        status_label.configure(
            text="🧪 Test Mode — simulate the terminal's response:",
            text_color=colors.TEXT_LIGHT
        )

        ctk.CTkButton(
            action_frame, text="✅ Approve", width=110, fg_color=colors.SUCCESS,
            hover_color=colors.SUCCESS_HOVER, font=colors.FONT_BUTTON,
            command=lambda: run_charge("approved")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_frame, text="❌ Decline", width=110, fg_color=colors.DANGER,
            hover_color=colors.DANGER_HOVER, font=colors.FONT_BUTTON,
            command=lambda: run_charge("declined")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_frame, text="✖ Cancel", width=100, fg_color=colors.SIDEBAR_BUTTON,
            font=colors.FONT_BUTTON,
            command=lambda: run_charge("cancelled")
        ).pack(side="left", padx=5)

        action_frame.pack(pady=6)

    # Brief "connecting" beat before the (simulated) terminal is ready,
    # so it reads like a real handshake rather than an instant popup.
    modal.after(900, reveal_test_controls)

    def on_close():
        run_charge("cancelled")

    modal.protocol("WM_DELETE_WINDOW", on_close)
