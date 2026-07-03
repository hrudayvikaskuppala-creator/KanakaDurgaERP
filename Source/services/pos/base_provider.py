"""
===========================================
 POS Provider Base Interface
===========================================
Every POS integration (a physical terminal SDK, a payment gateway's
"soft POS" API, etc.) implements this one interface. The Sales page
never talks to hardware/SDKs directly - it only calls
`provider.charge(...)`, so swapping in a real provider later (Pine
Labs, Razorpay POS, PayTM, an ESP32-based custom terminal, whatever
Kanakadurga Enterprises ends up using) is a matter of writing one new
class here and registering it in pos/manager.py - nothing in the
Sales page has to change.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class POSResult:
    success: bool
    status: str                        # "approved" | "declined" | "cancelled" | "error"
    transaction_id: Optional[str] = None
    approval_code: Optional[str] = None
    reference_no: Optional[str] = None
    message: str = ""


class POSProvider:
    """
    Subclass this and implement `charge()` for a real terminal/gateway.
    `provider_name` is stored on every transaction record so reports
    can tell which POS system processed a given payment.
    """
    provider_name = "base"

    def charge(self, amount, payment_mode, invoice_no, on_status=None):
        """
        amount: float, the exact amount to charge.
        payment_mode: "UPI" | "Credit Card" | "Debit Card" | "QR Code" | ...
        invoice_no: used as the order/reference id sent to the terminal.
        on_status(text): optional callback to report progress back to
            the UI (e.g. "Waiting for card...", "Processing...").

        Must return a POSResult. Must never raise - catch provider/SDK
        exceptions internally and return POSResult(success=False,
        status="error", message=...) instead, so the Sales page can
        always show a clean error rather than crashing.
        """
        raise NotImplementedError
