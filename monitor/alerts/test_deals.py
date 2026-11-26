from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Campaign, Deal

class DealTests(TestCase):
    def test_feed_threshold_dedup_and_isolation(self):
        user = get_user_model().objects.create_user("deal-owner")
        other = get_user_model().objects.create_user("deal-other")
        campaign = Campaign.objects.create(owner=user, name="Holiday", retailer="Example", category="Camping", event="Sale", starts_on=date(2026,11,25), ends_on=date(2026,12,1))
        path = f"/campaigns/{campaign.pk}/deals/"
        self.client.force_login(user)
        data = dict(title="Tent", url="https://example.com/tent", price="60", reference_price="100")
        self.assertEqual(self.client.post(path, data).status_code, 302)
        self.assertContains(self.client.get(path), "Tent")
        data["price"] = "90"
        self.assertEqual(self.client.post(path, data).status_code, 302)
        self.assertEqual(Deal.objects.count(), 1)
        self.assertNotContains(self.client.get(path), "Tent")
        data["price"] = "110"
        self.assertEqual(self.client.post(path, data).status_code, 200)
        self.client.force_login(other)
        self.assertEqual(self.client.get(path).status_code, 404)
        self.assertEqual(self.client.post(path, data).status_code, 404)
