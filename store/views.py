from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django import forms
from .models import Product, Category, Order, OrderItem


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "store/product_detail.html", {"product": product})

def _get_cart(session): return session.setdefault("cart", {})

def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)
    cart = _get_cart(request.session)
    pid = str(product.id)
    item = cart.get(pid, {"name": product.name, "price": str(product.price), "qty": 0, "slug": product.slug})
    if item["qty"] + 1 > product.stock:
        messages.warning(request, f"Only {product.stock} left for {product.name}.")
    else:
        item["qty"] += 1
        cart[pid] = item
        request.session.modified = True
        messages.success(request, f"Added {product.name} to cart")
    return redirect("home")

def remove_from_cart(request, pid):
    cart = _get_cart(request.session)
    if pid in cart:
        del cart[pid]
        request.session.modified = True
    return redirect("view_cart")

def inc_qty(request, pid):
    product = get_object_or_404(Product, pk=int(pid))
    cart = _get_cart(request.session)
    item = cart.get(pid)
    if item and item["qty"] + 1 <= product.stock:
        item["qty"] += 1
        cart[pid] = item
        request.session.modified = True
    return redirect("view_cart")

def dec_qty(request, pid):
    cart = _get_cart(request.session)
    if pid in cart:
        cart[pid]["qty"] -= 1
        if cart[pid]["qty"] <= 0:
            del cart[pid]
        request.session.modified = True
    return redirect("view_cart")

class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    address = forms.CharField(max_length=255)
    city = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    email = forms.EmailField()

def view_cart(request):
    return render(request, "store/cart.html", {"cart": request.session.get("cart", {})})


