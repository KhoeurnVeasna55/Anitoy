from django.shortcuts import render, redirect
from django.contrib import messages
from ..form import CheckoutForm
from ..models import Order, OrderItem
from ..services import cart as cart_svc

def checkout(request):
    cart, _, total_price = cart_svc.summary(request.session)
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("home")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(**form.cleaned_data, user=request.user if request.user.is_authenticated else None)
            for pid, item in cart.items():
                OrderItem.objects.create(order=order, product_id=int(pid), quantity=item["qty"], unit_price=item["price"])
            request.session["cart"] = {}
            messages.success(request, f"Order #{order.pk} placed! (demo)")
            return redirect("home")
    else:
        form = CheckoutForm()

    return render(request, "store/checkout.html", {"form": form, "cart": cart, "total_price": total_price})
