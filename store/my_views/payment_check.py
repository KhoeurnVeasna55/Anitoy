from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ..models import Order
from ..services.bakong import check_transaction_by_md5
from ..services.telegram_notify import send_paid_order_telegram


def check_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # already paid → ensure telegram sent once
    if order.payment_status == "PAID":
        if not order.telegram_paid_notified:
            send_paid_order_telegram(order)
        return JsonResponse({"ok": True, "status": "PAID"})

    if not order.khqr_md5:
        return JsonResponse({"ok": False, "status": "NO_MD5"})

    try:
        res = check_transaction_by_md5(order.khqr_md5)
    except Exception as e:
        return JsonResponse({"ok": False, "status": "ERROR", "error": str(e)})

    code = res.get("responseCode")
    data = res.get("data")

    if str(code) in ("0", "00") and data:
        order.payment_status = "PAID"
        order.paid_at = timezone.now()
        order.save(update_fields=["payment_status", "paid_at"])

        if not order.telegram_paid_notified:
            send_paid_order_telegram(order)

        return JsonResponse({"ok": True, "status": "PAID"})

    return JsonResponse({"ok": True, "status": "PENDING"})
