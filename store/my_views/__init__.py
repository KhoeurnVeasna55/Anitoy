# so you can `from . import views` and use views.HomeView, views.add_to_cart, etc.
from .catalog import home, product_detail
from .cart import view_cart, add_to_cart, remove_from_cart, inc_qty, dec_qty
from .auth import register
from .checkout import checkout
