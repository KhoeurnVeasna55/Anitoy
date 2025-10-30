from decimal import Decimal

def _get(session):
    return session.setdefault("cart", {})

def add(session, product, qty=1):
    cart = _get(session)
    pid = str(product.id)
    item = cart.get(pid, {"name": product.name, "price": str(product.price), "qty": 0, "slug": product.slug})
    item["qty"] += qty
    cart[pid] = item
    session.modified = True

def remove(session, pid):
    cart = _get(session)
    if pid in cart:
        del cart[pid]
        session.modified = True

def inc(session, product):
    add(session, product, 1)

def dec(session, pid):
    cart = _get(session)
    if pid in cart:
        cart[pid]["qty"] -= 1
        if cart[pid]["qty"] <= 0:
            del cart[pid]
        session.modified = True

def summary(session):
    cart = session.get("cart", {})
    total_qty = sum(i["qty"] for i in cart.values())
    total_price = sum(Decimal(i["price"]) * i["qty"] for i in cart.values())
    return cart, total_qty, total_price
