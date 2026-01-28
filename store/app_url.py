# store/urls.py
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.contrib.auth import views as auth_views

from .form import SignUpForm
from .my_views import (
    home,
    product_detail,
    view_cart,
    add_to_cart,
    remove_from_cart,
    inc_qty,
    dec_qty,
    checkout,
    register_view,
    login_view,
    logout_view,
)
from .my_views.checkout import payment_page

from .my_views.views_product_list import product_list
from .my_views.pload_payment import upload_payment
from .my_views.khqr_qr_image import khqr_qr_image
from .my_views.payment_check import check_payment
from .my_views.payment_success import payment_success


urlpatterns = [
    path("", home, name="home"),

    # Cart
    path("cart/", view_cart, name="view_cart"),
    path("cart/add/<slug:slug>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:pid>/", remove_from_cart, name="remove_from_cart"),
    path("cart/inc/<int:pid>/", inc_qty, name="inc_qty"),
    path("cart/dec/<int:pid>/", dec_qty, name="dec_qty"),

    # Catalog / Products
    path("catalog/", home, name="catalog"),
    path("products/", product_list, name="product_list"),
    path("product/<slug:slug>/", product_detail, name="product_detail"),

    # Checkout
    path("checkout/", checkout, name="checkout"),
    path("payment/<int:order_id>/", payment_page, name="payment_page"),
    path("payment/<int:order_id>/qr.png", khqr_qr_image, name="khqr_qr_image"),
    path("payment/check/<int:order_id>/", check_payment, name="check_payment"),
    path("payment/success/<int:order_id>/", payment_success, name="payment_success"),

    # Auth
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
