from io import BytesIO
import qrcode

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from ..models import Order

def khqr_qr_image(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    payload = order.khqr_qr or ""
    if not payload:
        return HttpResponse("KHQR not generated", status=404)

    img = qrcode.make(payload)

    buf = BytesIO()
    img.save(buf, format="PNG")
    return HttpResponse(buf.getvalue(), content_type="image/png")
