from __future__ import annotations

from asgiref.sync import async_to_sync
from django.test import TestCase

from apps.products.models import Product, TopProduct
from bot.handlers.menu import month_name
from bot.i18n import LANGUAGES
from bot.services import product_service


class TopProductTests(TestCase):
    def setUp(self):
        self.first = Product.objects.create(
            name="Serum", is_top=True, top_order=2, top_note="Eng ko'p sotilgan"
        )
        self.second = Product.objects.create(name="Krem", is_top=True, top_order=1)
        Product.objects.create(name="Toner")  # not in the top list

    def test_only_flagged_products_are_returned_in_order(self):
        top = async_to_sync(product_service.get_top_products)()
        self.assertEqual([p.name for p in top], ["Krem", "Serum"])

    def test_a_deactivated_product_drops_out_of_the_top_list(self):
        # The shop switches a product off when it stops selling it; forgetting
        # to untick "top" must not keep advertising it.
        Product.objects.filter(pk=self.first.pk).update(is_active=False)
        top = async_to_sync(product_service.get_top_products)()
        self.assertEqual([p.name for p in top], ["Krem"])

    def test_an_empty_top_list_is_a_normal_state(self):
        Product.objects.update(is_top=False)
        self.assertEqual(async_to_sync(product_service.get_top_products)(), [])

    def test_the_proxy_page_shows_exactly_the_flagged_products(self):
        self.assertEqual(TopProduct.objects.count(), 2)
        self.assertEqual(Product.objects.count(), 3)

    def test_translations_fall_back_to_uzbek(self):
        from core.i18n import pick

        product = Product.objects.create(name="Maska", name_ru="Маска")
        self.assertEqual(pick(product, "name", "ru"), "Маска")
        self.assertEqual(pick(product, "name", "en"), "Maska")


class MonthNameTests(TestCase):
    def test_every_language_names_the_current_month(self):
        for code in LANGUAGES:
            with self.subTest(language=code):
                self.assertTrue(month_name(code).strip())

    def test_unknown_language_falls_back_rather_than_raising(self):
        self.assertTrue(month_name("fr").strip())
