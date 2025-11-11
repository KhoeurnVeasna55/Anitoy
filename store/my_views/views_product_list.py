# store/views_product_list.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from django.db.models import Q
from ..models import Product, Category


def product_list(request):
    q = request.GET.get("q", "").strip()
    cat_slug = request.GET.get("cat")

    qs = Product.objects.filter(is_active=True).select_related("category").prefetch_related("images")

    current_cat = None
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    if cat_slug:
        current_cat = get_object_or_404(Category, slug=cat_slug)
        qs = qs.filter(category=current_cat)

    paginator = Paginator(qs.order_by("-created_at"), 12)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    return render(request, "pages/product_list.html", {
        "products": products,
        "current_cat": current_cat,
        "q": q,
    })
