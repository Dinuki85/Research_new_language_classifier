from typing import Any, Dict, Optional

MIN_PRODUCT_NAME_LENGTH = 5
MIN_STOCK_LEVEL = 1
MAX_ORDER_QUANTITY = 100

VALID_PAYMENT_METHODS = {"card", "paypal", "bank_transfer"}
VALID_MEMBERSHIP_TYPES = {"standard", "silver", "gold", "platinum"}

DELIVERY_CHARGES = {
    "standard": 8.99,
    "express": 15.99,
    "same_day": 25.00,
}

MEMBERSHIP_DISCOUNTS = {
    "standard": 0.00,
    "silver": 0.05,
    "gold": 0.10,
    "platinum": 0.20,
}

TAX_PERCENTAGE = 0.075


def process_online_order_and_generate_invoice(
    order_data: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Validate an online order, calculate discounts, taxes and delivery
    charges, then generate an invoice.

    Args:
        order_data:
            Dictionary containing customer, items, payment and delivery
            information.

    Returns:
        Dictionary containing order status, invoice details and summary.
    """

    if order_data is None:
        return {
            "status": "failed",
            "message": "Order data cannot be null",
            "invoice_id": None,
        }

    customer = order_data.get("customer")

    if not isinstance(customer, dict):
        return {
            "status": "failed",
            "message": "Missing customer information",
            "invoice_id": None,
        }

    customer_id = customer.get("customer_id")
    membership = customer.get("membership")

    if not isinstance(customer_id, str) or customer_id.strip() == "":
        return {
            "status": "failed",
            "message": "Invalid customer ID",
            "invoice_id": None,
        }

    if membership not in VALID_MEMBERSHIP_TYPES:
        return {
            "status": "failed",
            "message": "Invalid membership type",
            "invoice_id": None,
        }

    items = order_data.get("items")

    if not isinstance(items, list) or len(items) == 0:
        return {
            "status": "failed",
            "message": "Order must contain at least one item",
            "invoice_id": None,
        }

    subtotal = 0.0
    total_quantity = 0
    total_products = 0

    for product in items:

        if not isinstance(product, dict):
            return {
                "status": "failed",
                "message": "Invalid product format",
                "invoice_id": None,
            }

        product_name = product.get("product_name")
        price = product.get("price")
        quantity = product.get("quantity")
        stock = product.get("stock")

        if (
            not isinstance(product_name, str)
            or len(product_name) < MIN_PRODUCT_NAME_LENGTH
        ):
            return {
                "status": "failed",
                "message": "Invalid product name",
                "invoice_id": None,
            }

        if not isinstance(price, (int, float)) or price <= 0:
            return {
                "status": "failed",
                "message": "Invalid product price",
                "invoice_id": None,
            }

        if not isinstance(quantity, int) or quantity <= 0:
            return {
                "status": "failed",
                "message": "Invalid order quantity",
                "invoice_id": None,
            }

        if quantity > MAX_ORDER_QUANTITY:
            return {
                "status": "failed",
                "message": "Quantity exceeds maximum allowed limit",
                "invoice_id": None,
            }

        if not isinstance(stock, int) or stock < MIN_STOCK_LEVEL:
            return {
                "status": "failed",
                "message": f"Product {product_name} is out of stock",
                "invoice_id": None,
            }

        item_total = price * quantity

        if quantity >= 10:
            item_total = item_total * 0.90

        subtotal += item_total
        total_quantity += quantity
        total_products += 1

    discount_rate = MEMBERSHIP_DISCOUNTS[membership]
    membership_discount = subtotal * discount_rate
    discounted_total = subtotal - membership_discount

    payment = order_data.get("payment")

    if not isinstance(payment, dict):
        return {
            "status": "failed",
            "message": "Payment information missing",
            "invoice_id": None,
        }

    payment_method = payment.get("method")

    if payment_method not in VALID_PAYMENT_METHODS:
        return {
            "status": "failed",
            "message": "Unsupported payment method",
            "invoice_id": None,
        }

    delivery_type = order_data.get("delivery_type", "standard")

    if delivery_type not in DELIVERY_CHARGES:
        return {
            "status": "failed",
            "message": "Invalid delivery option",
            "invoice_id": None,
        }

    delivery_charge = DELIVERY_CHARGES[delivery_type]

    if discounted_total >= 200:
        delivery_charge = 0.0

    tax_amount = discounted_total * TAX_PERCENTAGE

    final_amount = (
        discounted_total
        + delivery_charge
        + tax_amount
    )

    invoice_id = (
        "INV-"
        + customer_id.upper()
        + "-"
        + str(total_products)
    )

    return {
        "status": "success",
        "message": "Order processed successfully",
        "invoice_id": invoice_id,
        "customer": {
            "customer_id": customer_id,
            "membership": membership,
        },
        "order_summary": {
            "total_products": total_products,
            "total_quantity": total_quantity,
            "subtotal": round(subtotal, 2),
            "membership_discount": round(membership_discount, 2),
            "delivery_charge": round(delivery_charge, 2),
            "tax": round(tax_amount, 2),
            "final_amount": round(final_amount, 2),
        },
        "payment": {
            "method": payment_method,
            "status": "approved",
        },
    }