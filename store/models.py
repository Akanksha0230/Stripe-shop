from django.db import models

# Create your models here.
class Product(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    price_cents = models.PositiveIntegerField()
    def __str__(self):
        return f"{self.name} (${self.price_cents/100:.2f})"
    
    @property
    def price_dollars(self):
        return "{:.2f}".format(self.price_cents/100)
 

class Order(models.Model):
    stripe_session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    total_cents = models.PositiveIntegerField(default=0)

    @property
    def total_dollars(self):
        return "{:.2f}".format(self.total_cents/100)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product =models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity= models.PositiveIntegerField()
    unit_price_cents= models.PositiveIntegerField()

    @property
    def total_price_dollars(self):
        return "{:.2f}".format(self.unit_price_cents * self.quantity /100)