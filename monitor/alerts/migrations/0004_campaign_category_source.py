from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("alerts", "0003_deal")]
    operations = [migrations.AddField(model_name="campaign", name="category_source", field=models.JSONField(default=dict, blank=True))]
