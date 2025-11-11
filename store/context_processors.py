# shop/context_processors.py
from decimal import Decimal
from .models import Category


def cart_summary(request):
    cart = request.session.get("cart", {})
    total_qty = 0
    total_price = Decimal("0.00")

    for _pid, item in cart.items():
        qty = int(item.get("qty", 0) or 0)
        price = Decimal(str(item.get("price", "0")))
        total_qty += qty
        total_price += price * qty

    return {
        "cart_total_qty": total_qty,
        "cart_total_price": total_price,
    }


def global_shop(request):
    return {
        "categories": Category.objects.order_by("name"),
    }
