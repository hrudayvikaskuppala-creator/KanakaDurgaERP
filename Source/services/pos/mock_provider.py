"""
===========================================
 Mock POS Provider
===========================================
Simulates a physical POS terminal so the whole "charge -> approve or
decline -> save/print automatically" flow can be built, tested, and
used today, without Kanakadurga Enterprises having a specific POS
terminal SDK wired in yet.

Honesty note: no real card/UPI network is contacted here - this
provider does not process real money. When a real terminal/gateway
(Pine Labs, Razorpay POS, PayTM, etc.) is chosen, its SDK gets its
own provider class (implementing the same POSProvider interface -
see base_provider.py) and gets registered in pos/manager.py; nothing
in the Sales page needs to change when that happens.

`simulate_decision` lets the caller (the Sales page's "simulated
terminal" popup) supply the outcome, since there's no real hardware
to report one - a real provider would get this from the terminal/SDK
instead of a function argument.
"""

import random
import string
import time
import uuid

from services.pos.base_provider import POSProvider, POSResult


class MockPOSProvider(POSProvider):
    provider_name = "Mock POS Terminal (Simulated)"

    def charge(self, amount, payment_mode, invoice_no, on_status=None, simulate_decision=None):
        try:
            if on_status:
                on_status("Connecting to POS terminal...")
            time.sleep(0.4)

            if on_status:
                on_status(f"Requesting ₹{amount:,.2f} via {payment_mode}...")
            time.sleep(0.4)

            decision = (simulate_decision or (lambda: "approved"))()

            if decision == "approved":
                return POSResult(
                    success=True,
                    status="approved",
                    transaction_id=f"MOCKPOS-{uuid.uuid4().hex[:10].upper()}",
                    approval_code="".join(random.choices(string.digits, k=6)),
                    reference_no=f"REF-{invoice_no}-{int(time.time())}",
                    message=f"Payment of ₹{amount:,.2f} approved via {payment_mode}."
                )

            if decision == "declined":
                return POSResult(
                    success=False,
                    status="declined",
                    message="The POS terminal declined this payment. "
                            "Please try a different card/UPI app, or a different payment mode."
                )

            return POSResult(
                success=False,
                status="cancelled",
                message="Payment was cancelled before it completed."
            )

        except Exception as exc:
            return POSResult(
                success=False,
                status="error",
                message=f"Could not reach the POS terminal.\n\nDetails: {exc}"
            )
