from ..models import OrderItem
from .telegram import send_telegram_message


def send_paid_order_telegram(order):
    items = OrderItem.objects.filter(order=order).select_related("product")

    items_lines = []
    items_count = 0
    total = 0.0

    for it in items:
        name = getattr(it.product, "name", f"Product #{it.product_id}")
        qty = int(it.quantity)
        price = float(it.unit_price)
        line_total = qty * price

        items_count += qty
        total += line_total
        items_lines.append(f"• {name} x{qty} = {line_total:.2f}")

    msg = (
        f"✅ <b>Payment Successful</b>\n"
        f"🧾 Order ID: <b>{order.id}</b>\n"
        f"👤 Name: <b>{order.full_name}</b>\n"
        f"📞 Phone: <b>{order.phone}</b>\n"
        f"📍 Address: <b>{order.address}</b>\n"
        f"📦 Items: <b>{items_count}</b>\n"
        f"💰 Total: <b>{total:.2f}</b>\n\n"
        f"<b>Items</b>\n" + "\n".join(items_lines)
    )

    # send telegram
    send_telegram_message(msg)

    # mark as notified
    order.telegram_paid_notified = True
    order.save(update_fields=["telegram_paid_notified"])
