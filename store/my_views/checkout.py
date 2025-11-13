from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..form import CheckoutForm, UploadPaymentForm
from ..models import Order, OrderItem
from ..services import cart as cart_svc
from django.contrib.auth.decorators import login_required
import json


@login_required(login_url='login')
def checkout(request):
    cart, _, total_price = cart_svc.summary(request.session)

    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("view_cart")

    # FIRST POST FROM CART (LOAD CHECKOUT PAGE)
    if request.method == "POST" and "full_name" not in request.POST:
        raw = request.POST.get("selected_items", "[]")
        print("FIRST POST RAW:", raw)

        request.session["selected_items_json"] = raw
        return render(request, "pages/checkout.html", {
            "form": CheckoutForm(),
            "cart": cart,
            "total_price": total_price,
        })

    # SECOND POST (CHECKOUT FORM SUBMIT)
    if request.method == "POST":
        raw = request.session.get("selected_items_json", "[]")
        print("SECOND POST RAW:", raw)

        selected_ids = json.loads(raw)

        if not selected_ids:
            messages.warning(request, "No items selected.")
            return redirect("view_cart")

        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                **form.cleaned_data,
                user=request.user
            )

            for pid in selected_ids:
                item = cart.get(str(pid))
                if item:
                    OrderItem.objects.create(
                        order=order,
                        product_id=pid,
                        quantity=item["qty"],
                        unit_price=item["price"]
                    )

            for pid in selected_ids:
                cart.pop(str(pid), None)
            request.session["cart"] = cart

            return redirect("payment_page", order_id=order.id)

    return render(request, "pages/checkout.html", {
        "form": CheckoutForm(),
        "cart": cart,
        "total_price": total_price,
    })


def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    upload_form = UploadPaymentForm()

    return render(request, "pages/payment_page.html", {
        "order": order,
        "upload_form": upload_form,
    })
