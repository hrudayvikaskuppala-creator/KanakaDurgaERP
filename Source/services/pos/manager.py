"""
===========================================
 POS Manager
===========================================
Central place that decides which POS provider is active. Today only
the Mock provider is registered; adding a real one later is:

    1. Write a new class in services/pos/<name>_provider.py that
       implements POSProvider.charge(...) (see base_provider.py).
    2. Add it to PROVIDERS below.
    3. Change ACTIVE_PROVIDER to its key (or make it a Settings-page
       dropdown if multiple real providers need to be switchable).

DIGITAL_PAYMENT_MODES lists which Sales page payment modes should go
through the POS terminal at all - Cash stays a simple direct save.
"""

from services.pos.mock_provider import MockPOSProvider

PROVIDERS = {
    "mock": MockPOSProvider,
    # "pinelabs": PineLabsProvider,      # example of a future real provider
    # "razorpay_pos": RazorpayPOSProvider,
}

ACTIVE_PROVIDER = "mock"

DIGITAL_PAYMENT_MODES = {"UPI", "Credit Card", "Debit Card", "QR Code"}


def get_active_provider():
    provider_class = PROVIDERS.get(ACTIVE_PROVIDER, MockPOSProvider)
    return provider_class()


def requires_pos(payment_mode):
    return (payment_mode or "").strip() in DIGITAL_PAYMENT_MODES
