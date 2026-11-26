from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators

class Migration(migrations.Migration):
    dependencies = [("alerts", "0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="Campaign", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("name", models.CharField(max_length=200)),
        ("retailer", models.CharField(max_length=100)),
        ("category", models.CharField(max_length=100)),
        ("event", models.CharField(max_length=100)),
        ("minimum_discount", models.PositiveSmallIntegerField(default=30, validators=[django.core.validators.MaxValueValidator(100)])),
        ("starts_on", models.DateField()),
        ("ends_on", models.DateField()),
        ("enabled", models.BooleanField(default=True)),
        ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
    ])]
