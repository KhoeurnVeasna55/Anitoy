from decimal import Decimal

def cart_summary(request):
    cart = request.session.get('cart', {})
    total_qty = sum(item.get('qty', 0) for item in cart.values())
    total_price = sum(Decimal(str(item.get('price', 0))) * item.get('qty', 0) for item in cart.values())
    return {"cart_total_qty": total_qty, "cart_total_price": total_price}
