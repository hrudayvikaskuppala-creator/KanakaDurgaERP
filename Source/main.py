"""
===========================================
 BatteryERP Professional
 Main Application Entry Point
===========================================
"""

# ------------------------------
# System Database
# ------------------------------
from database.migrations import migrate

# ------------------------------
# User Authentication
# ------------------------------
from models.user import create_admin

# ------------------------------
# Business Tables
# ------------------------------
from models.customer import create_customer_table
from models.product import create_product_table
from models.supplier import create_supplier_table
from models.purchase import create_purchase_table
from models.sales import create_sales_table
from models.pos_transaction import create_pos_transactions_table

# ------------------------------
# UI
# ------------------------------
from ui.login import open_login


def initialize_database():
    """
    Initialize all required database tables
    """

    print("=" * 50)
    print("Starting BatteryERP Professional...")
    print("=" * 50)

    # System Tables
    migrate()

    # Default Admin User
    create_admin()

    # Business Tables
    create_customer_table()
    create_product_table()
    create_supplier_table()
    create_purchase_table()
    create_sales_table()
    create_pos_transactions_table()

    print("Database Initialized Successfully.")
    print("=" * 50)


def start_application():
    """
    Start Login Window
    """
    open_login()


def main():
    initialize_database()
    start_application()


if __name__ == "__main__":
    main()