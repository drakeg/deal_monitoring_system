from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal

class Migration(migrations.Migration):
    dependencies = [("alerts", "0002_campaign")]
    operations = [migrations.CreateModel(name="Deal", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("title", models.CharField(max_length=300)),
        ("url", models.URLField(max_length=2000)),
        ("price", models.DecimalField(max_digits=12, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
        ("reference_price", models.DecimalField(max_digits=12, decimal_places=2, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
        ("observed_at", models.DateTimeField()),
        ("campaign", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="alerts.campaign")),
    ], options={"constraints": [models.UniqueConstraint(fields=("campaign", "url"), name="unique_campaign_deal_url")]})]
