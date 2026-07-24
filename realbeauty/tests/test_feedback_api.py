from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase

from apps.analytics.models import UserFeedback
from apps.products.models import Product
from apps.users.models import TelegramUser


class UserFeedbackApiTests(APITestCase):
    """
    The CRM "Mijozlar fikri" page needs to show *who* rated *what* without a
    separate lookup — raw ids in a table aren't "qulay tarzda ko'rish".
    """

    def setUp(self):
        self.client = APIClient()
        admin = get_user_model().objects.create_superuser("owner", "o@example.com", "pw")
        self.client.force_authenticate(admin)
        self.customer = TelegramUser.objects.create(
            telegram_id=9001, full_name="Dilnoza"
        )
        self.product = Product.objects.create(name="Face cream")

    def test_the_customer_and_product_names_are_included(self):
        UserFeedback.objects.create(
            user=self.customer, product=self.product, week=1, rating=5, text="Ajoyib"
        )
        response = self.client.get("/api/v1/feedback/")
        self.assertEqual(response.status_code, 200)
        row = response.data["results"][0]
        self.assertEqual(row["user_name"], "Dilnoza")
        self.assertEqual(row["product_name"], "Face cream")

    def test_a_feedback_with_no_product_shows_none_rather_than_crashing(self):
        UserFeedback.objects.create(user=self.customer, product=None, week=1, rating=3)
        response = self.client.get("/api/v1/feedback/")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data["results"][0]["product_name"])
