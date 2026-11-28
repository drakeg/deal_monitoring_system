from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("alerts", "0004_campaign_category_source")]
    operations = [
        migrations.AddField(model_name="campaign", name="last_scan_at", field=models.DateTimeField(null=True, blank=True)),
        migrations.AddField(model_name="campaign", name="last_scan_status", field=models.CharField(max_length=20, default="never")),
        migrations.AddField(model_name="campaign", name="last_scan_count", field=models.PositiveIntegerField(default=0)),
    ]
