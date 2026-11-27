from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Alert(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    product_url = models.URLField(max_length=2000)
    target_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Campaign(models.Model):
    category_source = models.JSONField(default=dict, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    retailer = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    event = models.CharField(max_length=100)
    minimum_discount = models.PositiveSmallIntegerField(default=30, validators=[MaxValueValidator(100)])
    starts_on = models.DateField()
    ends_on = models.DateField()
    enabled = models.BooleanField(default=True)

class Deal(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    url = models.URLField(max_length=2000)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    reference_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    observed_at = models.DateTimeField()

    class Meta:
        constraints = [models.UniqueConstraint(fields=("campaign", "url"), name="unique_campaign_deal_url")]

    @property
    def discount(self):
        return (self.reference_price - self.price) * 100 / self.reference_price
