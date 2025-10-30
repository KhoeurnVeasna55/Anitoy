from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import Product
from ..services import cart as cart_svc

def view_cart(request):
    cart, _, _ = cart_svc.summary(request.session)
    return render(request, "store/cart.html", {"cart": cart})

def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart = request.session.get("cart", {})
    before = cart.get(str(product.id), {}).get("qty", 0)
    cart_svc.add(request.session, product, 1)
    after = request.session.get("cart", {}).get(str(product.id), {}).get("qty", 0)
    if after == before:
        messages.warning(request, f"Only {product.stock} left for {product.name}.")
    else:
        messages.success(request, f"Added {product.name} to cart")
    return redirect("home")

def remove_from_cart(request, pid):
    cart_svc.remove(request.session, pid)
    return redirect("view_cart")

def inc_qty(request, pid):
    product = get_object_or_404(Product, pk=int(pid))
    cart_svc.inc(request.session, product)
    return redirect("view_cart")

def dec_qty(request, pid):
    cart_svc.dec(request.session, pid)
    return redirect("view_cart")
