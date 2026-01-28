from decimal import Decimal
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.urls import reverse
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import User


def unique_slugify(instance, source_value, slug_field="slug", extra_qs=None):
    base = slugify(source_value)[:200] or "item"
    slug = base
    Model = instance.__class__
    i = 2
    qs = Model.objects.all()
    if extra_qs is not None:
        qs = qs.filter(extra_qs)
    while qs.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base}-{i}"
        i += 1
        if len(slug) > 220:
            slug = slug[:220]
    return slug


# ---------- Category
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def clean(self):
        self.name = self.name.strip()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name, slug_field="slug")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ---------- Product
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)

    # pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    list_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_on_sale = models.BooleanField(default=False)

    # catalog/meta
    manufacturer = models.CharField(max_length=100, blank=True)
    series = models.CharField(max_length=120, blank=True)
    scale = models.CharField(max_length=20, blank=True)
    sku = models.CharField(max_length=64, unique=True, blank=True, null=True)
    barcode = models.CharField(max_length=64, blank=True)

    # availability
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_limited = models.BooleanField(default=False)
    is_preorder = models.BooleanField(default=False)
    release_date = models.DateField(null=True, blank=True)
    backorderable = models.BooleanField(default=False)

    # shipping dims (optional)
    weight_grams = models.PositiveIntegerField(default=0)
    length_mm = models.PositiveIntegerField(default=0)
    width_mm = models.PositiveIntegerField(default=0)
    height_mm = models.PositiveIntegerField(default=0)

    # media
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["category", "-created_at"]),
            models.Index(fields=["is_active", "is_preorder"]),
            models.Index(fields=["manufacturer"]),
            models.Index(fields=["name"]),
        ]

    # ---- Validation & lifecycle
    def clean(self):
        # Normalize strings
        self.name = self.name.strip()
        self.manufacturer = self.manufacturer.strip()
        self.series = self.series.strip()
        self.scale = self.scale.strip()
        self.barcode = self.barcode.strip()

        # Price logic
        if self.price < Decimal("0"):
            raise ValidationError({"price": "Price cannot be negative."})
        if self.list_price is not None and self.list_price < Decimal("0"):
            raise ValidationError({"list_price": "List price cannot be negative."})
        if self.is_on_sale:
            if not self.list_price:
                raise ValidationError({"list_price": "List price is required when item is on sale."})
            if self.list_price <= self.price:
                raise ValidationError({"price": "Sale price must be lower than list price."})

        # Stock/backorder sanity
        if self.stock == 0 and not self.backorderable and not self.is_preorder and self.is_active:
            # allowed, but you may choose to auto-disable; here we only warn via validation error if desired.
            pass

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name, slug_field="slug")
        super().save(*args, **kwargs)

    # ---- Pricing helpers
    def discount_amount(self):
        if self.is_on_sale and self.list_price and self.list_price > self.price:
            return self.list_price - self.price
        return Decimal("0.00")

    def discount_percent(self):
        if self.is_on_sale and self.list_price and self.list_price > self.price:
            return int(round((self.list_price - self.price) / self.list_price * 100))
        return 0

    def cover(self):

        if self.image:
            return self.image
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image
        first = self.images.first()
        return first.image if first else None

    def cover_url(self):
        img = self.cover()
        try:
            return img.url if img else ""
        except Exception:
            return ""

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])

    @property
    def is_in_stock(self):
        return self.stock > 0 or self.backorderable

    def __str__(self):
        return self.name

    def get_primary_image(self):
        """Return the best image (primary > sort_order > id)."""
        img = self.images.order_by("-is_primary", "sort_order", "id").first()
        return img

    def get_primary_image_url(self):
        img = self.get_primary_image()
        return img.image.url if img and img.image else static("img/placeholder.jpg")


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=150, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_primary", "sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_primary=True),
                name="unique_primary_image_per_product",
            )
        ]

    def clean(self):
        self.alt_text = self.alt_text.strip()
        # Skip the query when the parent product isn't saved yet
        if self.is_primary and self.product_id:
            existing = (
                ProductImage.objects
                .filter(product_id=self.product_id, is_primary=True)
                .exclude(pk=self.pk)
            )
            if existing.exists():
                raise ValidationError("Only one primary image is allowed per product.")

    def __str__(self):
        return f"{self.product.name} image #{self.pk or 'new'}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, default="-")  # ✅ default for old rows
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    email = models.EmailField()

    payment_screenshot = models.ImageField(upload_to="payments/", null=True, blank=True)

    # KHQR fields ---
    khqr_qr = models.TextField(blank=True, null=True)
    khqr_md5 = models.CharField(max_length=64, blank=True, null=True)
    telegram_paid_notified = models.BooleanField(default=False)

    # payment status for auto-check
    payment_status = models.CharField(
        max_length=20,
        default="PENDING",
        choices=[
            ("PENDING", "Pending"),
            ("PAID", "Paid"),
            ("FAILED", "Failed"),
        ],
    )
    paid_at = models.DateTimeField(blank=True, null=True)

    # verifi status
    VERIFY_STATUS = [
        ("pending", "Pending Verification"),
        ("verified", "Verified"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(max_length=20, choices=VERIFY_STATUS, default="pending")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["email"]),
            models.Index(fields=["payment_status"]),
        ]

    @property
    def total_amount(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Order #{self.pk}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
        ]

    def clean(self):
        if self.quantity < 1:
            raise ValidationError({"quantity": "Quantity must be at least 1."})
        if self.unit_price < Decimal("0"):
            raise ValidationError({"unit_price": "Unit price cannot be negative."})

    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

