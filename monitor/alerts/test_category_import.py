from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Campaign, Deal

class CategoryImportTests(TestCase):
    def test_authorized_import_deduplicates_and_isolates(self):
        owner = get_user_model().objects.create_user("import-owner")
        other = get_user_model().objects.create_user("import-other")
        campaign = Campaign.objects.create(owner=owner, name="Sale", retailer="Example", category="Camping", event="Holiday", starts_on=date(2026,11,25), ends_on=date(2026,12,1))
        path = f"/campaigns/{campaign.pk}/import/"
        item = '<article><h2>Tent</h2><b>$69.00</b><s>$119.00</s><a href="/tent">Link</a></article>'
        data = dict(listing_url="https://example.com/category", html=item+item+item.replace("/tent","https://other.example/tent"), item_selector="article", title_selector="h2::text", price_selector="b::text", reference_selector="s::text", url_selector="a::attr(href)")
        self.client.force_login(owner)
        self.client.post(path, data)
        self.assertEqual(Deal.objects.count(), 0)
        data["authorized"] = "on"
        for _ in range(2):
            self.assertContains(self.client.post(path, data), "Imported 1 valid products")
        self.assertEqual(Deal.objects.count(), 1)
        self.assertEqual(str(Deal.objects.get().price), "69.00")
        self.client.force_login(other)
        self.assertEqual(self.client.post(path, data).status_code, 404)
