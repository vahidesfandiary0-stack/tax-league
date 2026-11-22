from django.test import TestCase
from django.urls import reverse


class PublicLandingPageTests(TestCase):
    def test_homepage_is_public_and_renders_persian_branding(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "لیگ نخبگان مالیاتی")
        self.assertContains(response, "رقابت کن، رتبه بگیر، نخبه شو!")
