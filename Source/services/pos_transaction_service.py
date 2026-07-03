from models.pos_transaction import (
    save_pos_transaction,
    get_all_pos_transactions,
    get_pos_transactions_for_invoice
)


def record_transaction(invoice_no, amount, payment_mode, provider_name, result):
    """
    result: a POSResult from services.pos.base_provider.
    """
    save_pos_transaction(
        invoice_no,
        amount,
        payment_mode,
        provider_name,
        result.transaction_id,
        result.approval_code,
        result.reference_no,
        result.status,
        result.message
    )


def load_all_transactions():
    return get_all_pos_transactions()


def load_transactions_for_invoice(invoice_no):
    return get_pos_transactions_for_invoice(invoice_no)
