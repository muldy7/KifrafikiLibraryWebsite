from django.test import TestCase
from django.urls import reverse

# Create your tests here.
class BasicCoreTests(TestCase):
    """
    This class is for testing the basics of the core app and if all sites are accessible
    """
    def test_default_pages(self):
        """
        Test to see if basic pages are accessible
        """
        # test home 
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

        # test about
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

        # test the login page
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        