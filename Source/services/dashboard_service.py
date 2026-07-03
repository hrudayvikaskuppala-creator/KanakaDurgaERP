from database.database import fetchone


def get_dashboard_stats():

    stats = {}

    # Customers
    row = fetchone("SELECT COUNT(*) AS total FROM customers")
    stats["customers"] = row["total"] if row else 0

    # Products
    row = fetchone("SELECT COUNT(*) AS total FROM products")
    stats["products"] = row["total"] if row else 0

    # Suppliers
    row = fetchone("SELECT COUNT(*) AS total FROM suppliers")
    stats["suppliers"] = row["total"] if row else 0

    # Stock Value
    row = fetchone("""
        SELECT IFNULL(SUM(stock * selling_price),0) AS total
        FROM products
    """)
    stats["stock_value"] = row["total"] if row else 0

    # Low Stock
    row = fetchone("""
        SELECT COUNT(*) AS total
        FROM products
        WHERE stock <= min_stock
    """)
    stats["low_stock"] = row["total"] if row else 0

    return stats