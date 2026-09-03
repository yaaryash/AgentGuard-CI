orders = {
    "101": {
        "amount": 1000,
        "days_since_purchase": 5
    },
    "102": {
        "amount": 2500,
        "days_since_purchase": 45
    }
}


def get_order(order_id: str):
    return orders.get(order_id)


def check_refund_policy(order: dict):
    if order["days_since_purchase"] <= 30:
        return True

    return False


def create_refund(order_id: str, amount: float):
    return {
        "status": "success",
        "order_id": order_id,
        "refund_amount": amount
    }