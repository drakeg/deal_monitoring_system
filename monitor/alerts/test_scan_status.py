from datetime import timedelta
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone
from .models import Campaign

class ScanStatusTests(TestCase):
    def test_success_failure_and_paused(self):
        today = timezone.localdate()
        user = get_user_model().objects.create_user("status-owner")
        campaign = Campaign.objects.create(owner=user, name="Sale", retailer="Example", category="Camping", event="Sale", starts_on=today, ends_on=today+timedelta(days=1), category_source={"listing_url":"https://example.com/sale"})
        with patch("alerts.management.commands.collect_categories.fetch_category", return_value="<html></html>"), patch("alerts.management.commands.collect_categories.candidates", return_value=[]):
            call_command("collect_categories")
        campaign.refresh_from_db()
        self.assertEqual(campaign.last_scan_status, "empty")
        self.assertIsNotNone(campaign.last_scan_at)
        with patch("alerts.management.commands.collect_categories.fetch_category", side_effect=ValueError("blocked")):
            with self.assertRaises(CommandError):
                call_command("collect_categories")
        campaign.refresh_from_db()
        self.assertEqual(campaign.last_scan_status, "failed")
        campaign.enabled = False
        campaign.save()
        with patch("alerts.management.commands.collect_categories.fetch_category") as fetch:
            call_command("collect_categories")
            fetch.assert_not_called()
