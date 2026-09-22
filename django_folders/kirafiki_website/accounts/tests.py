from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

# Create your tests here.
class AccountsTests(TestCase):
    def test_user_creation(self):
        """
        Tests if the create an account page worls

        """
        url = reverse("accounts:signup") # including reverse in the url
                
        response = self.client.get((url))
        self.assertContains(response, "Create an Account")
