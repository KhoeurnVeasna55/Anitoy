from django.contrib import admin
from django.forms import BaseInlineFormSet
from django.utils.html import format_html

from .models import Category, Product, Order, OrderItem, ProductImage


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
            if not hasattr(form, "cleaned_data"):
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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "status",
        "payment_preview",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email")

    readonly_fields = ("created_at", "total_amount", "payment_preview")

    inlines = (OrderItemInline,)

    actions = ["mark_verified", "mark_rejected"]

    def mark_verified(self, request, queryset):
        updated = queryset.update(status="verified")
        self.message_user(request, f"{updated} order(s) marked as Verified.")

    def mark_rejected(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"{updated} order(s) marked as Rejected.")

    mark_verified.short_description = "Mark selected orders as Verified"
    mark_rejected.short_description = "Mark selected orders as Rejected"

    def payment_preview(self, obj):
        if obj.payment_screenshot:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height:70px; border-radius:6px; border:1px solid #ddd;">'
                "</a>",
                obj.payment_screenshot.url,
                obj.payment_screenshot.url,
            )
        return "No screenshot"
