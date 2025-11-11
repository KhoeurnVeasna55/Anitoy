# store/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .my_views import (
    home,
    product_detail,
    view_cart,
    add_to_cart,
    remove_from_cart,
    inc_qty,
    dec_qty,
    checkout,
    register,
)
from .my_views.views_product_list import product_list

urlpatterns = [
    path("", home, name="home"),

    path("cart/", view_cart, name="view_cart"),
    path("cart/add/<slug:slug>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pid>/", remove_from_cart, name="remove_from_cart"),
    path("cart/inc/<int:pid>/", inc_qty, name="inc_qty"),
    path("cart/dec/<int:pid>/", dec_qty, name="dec_qty"),

    path("catalog/", home, name="catalog"),
    path("checkout/", checkout, name="checkout"),

    # ✅ This now works!
    path("products/", product_list, name="product_list"),

    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),

    path("product/<slug:slug>/", product_detail, name="product_detail"),
]
