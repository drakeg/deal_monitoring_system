from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Alert(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    product_url = models.URLField(max_length=2000)
    target_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
