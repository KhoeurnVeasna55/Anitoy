from django.shortcuts import render, get_object_or_404
from ..models import Product, Category

def home(request):
    q = request.GET.get("q", "")
    cat = request.GET.get("cat")
    categories = Category.objects.order_by("name")
    current_cat = Category.objects.filter(slug=cat).first() if cat else None
    products = Product.objects.select_related("category").order_by("-created_at")
    if q:
        products = products.filter(name__icontains=q)
    if current_cat:
        products = products.filter(category=current_cat)
    return render(request, "pages/home.html", {
        "products": products, "categories": categories, "q": q, "current_cat": current_cat
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, "store/product_detail.html", {"product": product})
