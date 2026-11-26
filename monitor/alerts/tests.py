from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Alert

class AlertTests(TestCase):
    def test_multiple_alerts_and_owner_isolation(self):
        user = get_user_model().objects.create_user("one", password="test-password")
        other = get_user_model().objects.create_user("two", password="test-password")
        self.client.force_login(user)
        for name in ["Bike", "Solar"]:
            self.assertEqual(self.client.post("/", {"name":name,"product_url":"https://example.com/product","target_price":"100","enabled":"on"}).status_code,302)
        self.assertEqual(Alert.objects.filter(owner=user).count(),2)
        alert = Alert.objects.filter(owner=user).first()
        self.client.force_login(other)
        self.assertNotContains(self.client.get("/"), "Bike")
        self.assertEqual(self.client.post(f"/alerts/{alert.pk}/delete/").status_code,404)
    def test_login_required(self):
        self.assertEqual(self.client.get("/").status_code,302)
