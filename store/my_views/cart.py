from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from ..models import Product
from ..services import cart as cart_svc


def view_cart(request):
    session_cart = request.session.get("cart", {}) or {}

    pid_ints = []
    for pid_s in session_cart.keys():
        try:
            pid_ints.append(int(pid_s))
        except (TypeError, ValueError):
            continue

    # Fetch products (with category for display)
    products = (
        Product.objects.filter(id__in=pid_ints)
        .select_related("category")
        .prefetch_related("images")
    )
    prod_map = {p.id: p for p in products}

    items = []
    subtotal = Decimal("0.00")

    for pid_s, row in session_cart.items():
        try:
            pid = int(pid_s)
        except (TypeError, ValueError):
            continue

        product = prod_map.get(pid)
        if not product:
            # Product no longer exists; skip this line
            continue

        # qty
        try:
            qty = int(row.get("qty", 0) or 0)
        except (TypeError, ValueError):
            qty = 0

        unit_raw = row.get("price", None)
        try:
            unit_price = Decimal(str(unit_raw)) if unit_raw is not None else Decimal(str(product.price))
        except Exception:
            unit_price = Decimal(str(product.price))

        line_total = unit_price * qty
        subtotal += line_total

        items.append({
            "pid": pid,  # int for URL reversing
            "product": product,
            "qty": qty,
            "unit_price": unit_price,
            "line_total": line_total,
        })

    total = subtotal
    count = sum(i["qty"] for i in items)

    context = {
        "cart": {
            "items": items,
            "subtotal": subtotal,
            "total": total,
            "count": count,
        }
    }
    return render(request, "pages/cart.html", context)


@require_POST
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Quantity logic
    try:
        qty = int(request.POST.get("quantity", "1"))
    except ValueError:
        qty = 1
    qty = max(1, min(qty, 99))

    # Stock check
    if not product.is_preorder and product.stock is not None:
        qty = min(qty, max(product.stock, 0))

    # Add to cart
    before = request.session.get("cart", {}).get(str(product.id), {}).get("qty", 0)
    cart_svc.add(request.session, product, qty)
    after = request.session.get("cart", {}).get(str(product.id), {}).get("qty", 0)

    if after == before:
        if product.stock is not None:
            messages.warning(request, f"Only {product.stock} left for {product.name}.")
        else:
            messages.warning(request, f"Couldn’t add {product.name}.")
    else:
        messages.success(request, f"Added {qty} × {product.name} to cart")

    return redirect("view_cart")


@require_POST
def remove_from_cart(request, pid):
    # session keys are strings
    cart_svc.remove(request.session, str(pid))
    messages.info(request, "Removed item from cart.")
    return redirect("view_cart")


@require_POST
def inc_qty(request, pid):
    product = get_object_or_404(Product, pk=int(pid))
    cart_svc.inc(request.session, product)  # your service likely needs the Product
    return redirect("view_cart")


@require_POST
def dec_qty(request, pid):
    # many services accept pid-as-string for direct dict access
    cart_svc.dec(request.session, str(pid))
    return redirect("view_cart")
