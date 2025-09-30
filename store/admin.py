from django.contrib import admin
from .models import Product, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ("product", "quantity", "unit_price_cents")
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "stripe_session_id", "paid", "total_cents", "created_at")
    inlines = [OrderItemInline]

admin.site.register(Product)

# Register your models here.
