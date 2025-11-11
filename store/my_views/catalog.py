# store/my_views/catalog.py
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from ..models import Product, Category


def home(request):

    q = request.GET.get("q", "").strip()
    cat_slug = request.GET.get("cat")

    qs = Product.objects.select_related("category").prefetch_related("images").filter(is_active=True)

    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    current_cat = None
    if cat_slug:
        current_cat = get_object_or_404(Category, slug=cat_slug)
        qs = qs.filter(category=current_cat)

    # Paginate results
    paginator = Paginator(qs.order_by("-created_at"), 12)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    # Show hero only on pure home page (no search, no category, first page)
    show_hero = not q and not cat_slug and not page

    context = {
        "products": products,
        "q": q,
        "current_cat": current_cat,
        "show_hero": show_hero,
        # "categories": categories,
    }

    return render(request, "pages/index.html", context)


def product_detail(request, slug):
    """
    Display a single product detail page with related products.
    """
    product = get_object_or_404(
        Product.objects.select_related("category").prefetch_related("images"),
        slug=slug,
        is_active=True
    )

    # Get all images, primary first
    images = product.images.order_by("-is_primary", "sort_order", "id")

    # Get related products from same category
    related = (
        Product.objects
        .filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)
        .order_by("-created_at")[:8]
    )

    context = {
        "product": product,
        "images": images,
        "related": related,
    }

    return render(request, "pages/product_detail.html", context)