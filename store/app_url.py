from django.urls import path
from django.contrib.auth import views as auth_views
from .my_views import home, product_detail, view_cart, add_to_cart, remove_from_cart, inc_qty, dec_qty, checkout, register

urlpatterns = [
    path("", home, name="home"),
    path("p/<slug:slug>/", product_detail, name="product_detail"),
    path("cart/", view_cart, name="view_cart"),
    path("cart/add/<slug:slug>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<str:pid>/", remove_from_cart, name="remove_from_cart"),
    path("cart/inc/<str:pid>/", inc_qty, name="inc_qty"),
    path("cart/dec/<str:pid>/", dec_qty, name="dec_qty"),
    path("checkout/", checkout, name="checkout"),
    path("login/",  auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", register, name="register"),
]
