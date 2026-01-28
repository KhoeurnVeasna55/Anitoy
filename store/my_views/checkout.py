import json
import hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Order, OrderItem
from ..services import cart as cart_svc
from ..form import CheckoutForm
from bakong_khqr import KHQR


@login_required(login_url="login")
def checkout(request):
    cart, _, total_price = cart_svc.summary(request.session)

    if not cart:
        messages.info(request, "Your cart is empty.")
        return redirect("view_cart")

    # FIRST POST FROM CART (LOAD CHECKOUT PAGE)
    if request.method == "POST" and "full_name" not in request.POST:
        raw = request.POST.get("selected_items", "[]")
        request.session["selected_items_json"] = raw

        return render(request, "pages/checkout.html", {
            "form": CheckoutForm(),
            "cart": cart,
            "total_price": total_price,
        })

    # SECOND POST (FORM SUBMIT)
    if request.method == "POST":
        raw = request.session.get("selected_items_json", "[]")

        try:
            selected_ids = json.loads(raw)
        except Exception:
            selected_ids = []

        if not selected_ids:
            messages.warning(request, "No items selected.")
            return redirect("view_cart")

        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(request, "pages/checkout.html", {
                "form": form,
                "cart": cart,
                "total_price": total_price,
            })

        order = Order.objects.create(
            **form.cleaned_data,
            user=request.user,
            payment_status="PENDING",
        )

        # Create items
        for pid in selected_ids:
            item = cart.get(str(pid))
            if not item:
                continue

            qty = int(item.get("qty", 0))
            price = float(item.get("price", 0))

            OrderItem.objects.create(
                order=order,
                product_id=pid,
                quantity=qty,
                unit_price=price
            )

        # Remove selected from cart (keep your current behavior)
        for pid in selected_ids:
            cart.pop(str(pid), None)
        request.session["cart"] = cart
        request.session.pop("selected_items_json", None)

        return redirect("payment_page", order_id=order.id)

    # GET request
    return render(request, "pages/checkout.html", {
        "form": CheckoutForm(),
        "cart": cart,
        "total_price": total_price,
    })


def payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not order.khqr_qr or not order.khqr_md5:
        khqr = KHQR()
        amount = float(order.total_amount or 0)

        res = khqr.create_qr(
            bank_account="veasna_khoeurn1@bkrt",
            merchant_name="Veasna Khoeurn",
            merchant_city="Phnom Penh",
            currency="USD",
            store_label="Anitoys Shop",
            phone_number="855887925156",
            terminal_label="webQR",
            bill_number=str(order.id),
            amount=amount,
            static=False,
        )

        if isinstance(res, dict):
            qr_string = res.get("qr") or res.get("data", {}).get("qr") or ""
            md5_value = res.get("md5") or res.get("data", {}).get("md5") or ""
        else:
            qr_string = str(res)
            md5_value = hashlib.md5(qr_string.encode("utf-8")).hexdigest()

        order.khqr_qr = qr_string
        order.khqr_md5 = md5_value
        order.save(update_fields=["khqr_qr", "khqr_md5"])

    return render(request, "pages/payment_page.html", {"order": order})
