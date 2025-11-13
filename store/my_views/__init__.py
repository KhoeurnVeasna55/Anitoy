from .catalog import home, product_detail
from .cart import view_cart, add_to_cart, remove_from_cart, inc_qty, dec_qty
from .checkout import checkout
from .auth import register_view, logout_view, login_view

__all__ = [
    "home", "product_detail",
    "view_cart", "add_to_cart", "remove_from_cart", "inc_qty", "dec_qty",
    "checkout", "register_view","login_view", "logout_view",
]

