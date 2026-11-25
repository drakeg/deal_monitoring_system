from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator
from decimal import Decimal

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="Alert", fields=[
        ("id", models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name="ID")),
        ("name", models.CharField(max_length=200)),
        ("product_url", models.URLField(max_length=2000)),
        ("target_price", models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])),
        ("enabled", models.BooleanField(default=True)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
    ])]
