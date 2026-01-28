from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.utils.html import format_html

from .models import Category, Product, Order, OrderItem, ProductImage
from .services.bakong import check_transaction_by_md5
from .services.telegram_notify import send_paid_order_telegram

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ProductImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        primaries = 0
        for form in self.forms:
            if not getattr(form, "cleaned_data", None):
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("is_primary"):
                primaries += 1
        if primaries > 1:
            from django.core.exceptions import ValidationError
            raise ValidationError("Please select at most one primary image per product.")


class ProductImageLine(admin.TabularInline):
    model = ProductImage
    formset = ProductImageInlineFormSet
    fields = ("image", "alt_text", "is_primary", "sort_order")
    extra = 1
    ordering = ("-is_primary", "sort_order", "id")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("name", "slug", "category__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category",)
    readonly_fields = ("created_at",)
    inlines = (ProductImageLine,)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ("product",)
    fields = ("product", "quantity", "unit_price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone",
        "payment_status",
        "paid_at",
        "telegram_paid_notified",
        "khqr_preview",
        "total_amount_display",
        "created_at",
    )
    list_filter = ("payment_status", "telegram_paid_notified", "status", "created_at")
    search_fields = ("id", "full_name", "email", "phone", "khqr_md5")
    readonly_fields = (
        "created_at",
        "paid_at",
        "khqr_preview",
        "khqr_md5",
        "khqr_qr",
        "total_amount_display",
        "telegram_paid_notified",
        "payment_status",
    )

    inlines = (OrderItemInline,)

    actions = ["mark_verified", "mark_rejected", "force_mark_paid", "resend_paid_telegram"]

    def mark_verified(self, request, queryset):
        updated = queryset.update(status="verified")
        self.message_user(request, f"{updated} order(s) marked as Verified.")

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"{updated} order(s) marked as Rejected.")

    mark_verified.short_description = "Mark selected orders as Verified"
    mark_rejected.short_description = "Mark selected orders as Rejected"

    @admin.display(description="Total ($)")
    def total_amount_display(self, obj: Order):
        # works if total_amount is @property or method
        total = obj.total_amount if not callable(getattr(obj, "total_amount", None)) else obj.total_amount()
        try:
            return f"{float(total):.2f}"
        except Exception:
            return total

    @admin.display(description="KHQR QR")
    def khqr_preview(self, obj: Order):

        if not obj.khqr_qr:
            return "—"

        # This URL must exist in your urls.py:
        # path("khqr/<int:order_id>/qr.png", khqr_qr_image, name="khqr_qr_image")
        try:
            url = f"/khqr/{obj.id}/qr.png"
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height:80px;width:80px;border-radius:10px;border:1px solid #ddd;object-fit:contain;background:#fff;" />'
                "</a>",
                url,
                url,
            )
        except Exception:
            return "QR"

    def force_mark_paid(self, request, queryset):
        """
        Manual admin action if needed (for rare cases).
        """
        from django.utils import timezone
        updated = queryset.exclude(payment_status="PAID").update(payment_status="PAID", paid_at=timezone.now())
        self.message_user(request, f"{updated} order(s) set to PAID.")

    force_mark_paid.short_description = "Force mark as PAID (manual)"

    def resend_paid_telegram(self, request, queryset):
        from store.services.telegram_notify import send_paid_order_telegram

        sent = 0
        for order in queryset:
            if order.payment_status != "PAID":
                continue

            order.telegram_paid_notified = False
            order.save(update_fields=["telegram_paid_notified"])

            send_paid_order_telegram(order)
            sent += 1

        self.message_user(request, f"Telegram resent for {sent} paid order(s).")

