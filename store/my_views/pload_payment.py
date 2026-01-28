from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Order
from ..form import  UploadPaymentForm
from bakong_khqr import KHQR
@login_required(login_url="login")
def upload_payment(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)

    if request.method == "POST":
        form = UploadPaymentForm(request.POST, request.FILES, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment screenshot uploaded successfully!")
            return redirect("home")
    else:
        form = UploadPaymentForm(instance=order)

    return render(request, "pages/upload_payment.html", {"form": form, "order": order})


# khqr = KHQR()
# qr_string = khqr.create_qr(
#     bank_account="veasna_khoeurn1@bkrt",
#     merchant_name="Veasna Khoeurn",
#     merchant_city="Phnom Penh",
#     currency= "USDC",
#     store_label="Anitoys Shop",
#     phone_number="855887925156",
#     terminal_label="webQR",
#     bill_number="",
#      static=False
# )