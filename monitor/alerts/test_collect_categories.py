from unittest.mock import patch
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from alerts.models import Campaign, Deal

class CollectionTests(TestCase):
    def test_active_saved_source_only_and_deduplication(self):
        today = timezone.localdate()
        owner = get_user_model().objects.create_user(username="collector")
        fields = dict(owner=owner, name="Holiday", retailer="Example", category="Tools", event="Sale", starts_on=today, ends_on=today, category_source={"listing_url": "https://example.com/category"})
        active = Campaign.objects.create(**fields)
        Campaign.objects.create(**{**fields, "enabled": False})
        Campaign.objects.create(**{**fields, "starts_on": today-timedelta(days=2), "ends_on": today-timedelta(days=1)})
        row = dict(title="Tool", url="https://example.com/tool", price="10.00", reference_price="20.00")
        with patch("alerts.management.commands.collect_categories.fetch_category", return_value="<html></html>") as fetch, patch("alerts.management.commands.collect_categories.candidates", return_value=[row]):
            call_command("collect_categories")
            call_command("collect_categories")
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(Deal.objects.count(), 1)
        self.assertEqual(Deal.objects.get().campaign, active)
