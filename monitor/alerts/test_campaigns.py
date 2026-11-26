from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Campaign

class CampaignTests(TestCase):
    def test_creation_and_isolation(self):
        user = get_user_model().objects.create_user("campaign-owner")
        other = get_user_model().objects.create_user("campaign-other")
        self.client.force_login(user)
        data = dict(name="Holiday fitness", retailer="Walmart", category="Fitness", event="Black Friday", minimum_discount=30, starts_on="2026-11-25", ends_on="2026-12-01", enabled="on")
        self.assertEqual(self.client.post("/campaigns/", data).status_code, 302)
        campaign = Campaign.objects.get(owner=user)
        self.client.force_login(other)
        self.assertNotContains(self.client.get("/campaigns/"), campaign.name)
        self.assertEqual(self.client.post(f"/campaigns/{campaign.pk}/toggle/").status_code, 404)
        self.client.force_login(user)
        self.assertEqual(self.client.post(f"/campaigns/{campaign.pk}/toggle/").status_code, 302)
        campaign.refresh_from_db()
        self.assertFalse(campaign.enabled)
        data["ends_on"] = "2026-11-01"
        self.assertEqual(self.client.post("/campaigns/", data).status_code, 200)
        self.assertEqual(Campaign.objects.count(), 1)
