from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from .models import BugReport


# functions for testing
def create_user(self,username):
    """
    This function creates a user so it can be used with the form that requires a user sign in
    Can take different usernames for testing different users 
    """
    CustomUser = get_user_model()
    self.user = CustomUser.objects.create_user(username=username, password="password123")
    self.client.login(username=username, password="password123") # Log the user in!

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

    def test_no_login(self):
        """
        The use must be logged in to use the submit a bug form
        """
        # get url for the update entry page
        url = reverse_lazy("submit-a-bug") # including reverse in the url

        # now the user can't even access the page
        response = self.client.get(url)

        # user will be automatically redirected
        self.assertEqual(response.status_code, 302) # <--- 302 for a redirect
        #self.assertTemplateUsed(response, "core/login.html") 

    def test_user_added(self):
        """
        Testing if a successful save results in the user added to the bug report
        """
        # create a user for testing
        CustomUser = get_user_model()
        self.user = CustomUser.objects.create_user(username="test_user", password="password123")

        # log in the user
        self.client.login(username="test_user", password="password123") 

        # get url for the update entry page
        url = reverse_lazy("submit-a-bug") # including reverse in the url

        # now the user can't even access the page
        response = self.client.get(url)

        # see if the site is shown correctly
        self.assertEqual(response.status_code, 200) 
        self.assertTemplateUsed(response, "core/create_a_bug.html")

        # create some form data
        form_data = {"title": 'test title',
                     "summary": 'this is the bug report'}

        # post the data to the form
        response = self.client.post(url, data = form_data)

        # see if the user is redirected after submitting
        self.assertEqual(response.status_code, 302) 
        #self.assertTemplateUsed(response, "core/home.html") <--- to templates used on redirect
        #self.assertContains(response, "Bug submitted successfully. Thank you!")

        # see if the user is on the report
        report = BugReport.objects.get(title = 'test title')

        # see if the user is added
        self.assertEqual(self.user, report.author)

    def test_bad_values(self):
        """
        Test to see if the form allows bad values like nothing written or empty spaces
        """
        # create a user for testing
        CustomUser = get_user_model()
        self.user = CustomUser.objects.create_user(username="test_user", password="password123")

        # log in the user
        self.client.login(username="test_user", password="password123") 

        # get url for the update entry page
        url = reverse_lazy("submit-a-bug") # including reverse in the url

        # create some form data with nothing written
        form_data = {"title": '',
                    "summary": ''}

        # post the data to the form
        response = self.client.post(url, data = form_data)

        # see if the user is redirected after submitting
        self.assertEqual(response.status_code, 200) 

        # create some form data with just spaces nothing written
        form_data = {"title": '    ',
                    "summary": '   '}

        # post the data to the form
        response = self.client.post(url, data = form_data)

        # see if the user is redirected after submitting
        self.assertEqual(response.status_code, 200)

        # create some form data with random characters (the exact number can be changed later)
        form_data = {"title": '++++',
                    "summary": '123456787'}

        # post the data to the form
        response = self.client.post(url, data = form_data)

        # see if the user is redirected after submitting
        self.assertEqual(response.status_code, 200) 

"""
TESTS
1. no user denied (DONE)
2. have to submit something, no spaces (DONE)
3. successful entry means the user gets added (DONE)
"""