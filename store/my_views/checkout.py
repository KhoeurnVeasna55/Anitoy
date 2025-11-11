from django.shortcuts import render, redirect
from django.contrib import messages
from ..form import CheckoutForm
from ..models import Order, OrderItem
from ..services import cart as cart_svc


def checkout(request):
    cart, _, total_price = cart_svc.summary(request.session)
    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("view_cart")

    if request.method == "POST":
        selected_ids = request.POST.getlist("selected_items")
        if not selected_ids:
            messages.warning(request, "Please select at least one item to checkout.")
            return redirect("view_cart")

        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                **form.cleaned_data,
                user=request.user if request.user.is_authenticated else None
            )

            for pid in selected_ids:
                item = cart.get(pid)
                if item:
                    OrderItem.objects.create(
                        order=order,
                        product_id=int(pid),
                        quantity=item["qty"],
                        unit_price=item["price"]
                    )

            # remove only selected items from cart
            for pid in selected_ids:
                cart.pop(pid, None)

            request.session["cart"] = cart
            messages.success(request, f"Order #{order.pk} placed successfully! (Demo)")
            return redirect("home")
    else:
        form = CheckoutForm()

    return render(request, "pages/checkout.html", {
        "form": form,
        "cart": cart,
        "total_price": total_price
    })
