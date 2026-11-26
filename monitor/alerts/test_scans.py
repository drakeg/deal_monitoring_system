from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Campaign, Deal

class ScanTests(TestCase):
    def test_offline_scan_isolated_and_not_persisted(self):
        user = get_user_model().objects.create_user("scan-owner")
        other = get_user_model().objects.create_user("scan-other")
        campaign = Campaign.objects.create(owner=user, name="Demo", retailer="Example", category="Camping", event="Sale", starts_on=date(2026,11,25), ends_on=date(2026,12,1), minimum_discount=45)
        path = f"/campaigns/{campaign.pk}/scan/"
        self.client.force_login(user)
        self.assertEqual(self.client.get(path).status_code, 405)
        response = self.client.post(path)
        self.assertContains(response, "Demo exercise mat")
        self.assertNotContains(response, "Demo camping tent")
        self.assertContains(response, "fictional prices")
        self.assertEqual(Deal.objects.count(), 0)
        self.client.force_login(other)
        self.assertEqual(self.client.post(path).status_code, 404)
