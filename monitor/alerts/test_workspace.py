from datetime import date
from django.contrib.auth import get_user_model
from django.test import TestCase
from .models import Campaign

class WorkspaceTests(TestCase):
    def test_shared_navigation(self):
        user = get_user_model().objects.create_user("workspace-user")
        self.client.force_login(user)
        campaign = Campaign.objects.create(owner=user, name="Sale", retailer="Example", category="Camping", event="Holiday", starts_on=date(2026,11,25), ends_on=date(2026,12,1))
        for path in ("/", "/campaigns/", f"/campaigns/{campaign.pk}/deals/"):
            response = self.client.get(path)
            self.assertTemplateUsed(response, "workspace.html")
            self.assertContains(response, 'aria-current="page"', count=1)
            self.assertContains(response, "Sign out")
            self.assertContains(response, "Sale campaigns")
