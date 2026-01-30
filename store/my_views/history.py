from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Prefetch
from store.models import Order

@login_required
def order_history(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-id")
    )
    return render(request, "pages/order_history.html", {"orders": orders})
