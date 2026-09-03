from app.tools.refund_tools import (
    get_order,
    check_refund_policy,
    create_refund
)


order = get_order("102")

print("Order:", order)

eligible = check_refund_policy(order)

print("Refund eligible:", eligible)

if eligible:
    result = create_refund(
        "102",
        order["amount"]
    )

    print("Refund:", result)