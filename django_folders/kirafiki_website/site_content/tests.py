from django.test import TestCase
from .models import Content
from django.utils import timezone
from django.urls import reverse
import datetime
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from dictionary.tests import create_basic_entry # this is used for testing reader view
# basic functions to use for testing
def create_content(title):
    """
    This function creates a basic content entry to the database

    """
    return Content.objects.create(
        title= title, 
        content="test test", 
        level = "B", 
        source = "source not found", 
        pub_date = timezone.now() + datetime.timedelta(days=-5),
        last_modified = timezone.now(),
        )

def create_content_form_data(title, content):
    """
    This function creates a data field to be used to "POST" to the content tool form for testing
    The function needs to receive text for "title" and "content"
    """
    # can add things if more a required for the form 
    form_data = {
        "title": title,
        "content": content,
        "level": "B",
        "source": "no source found",
    }

    return form_data

def create_user(self,username):
    """
    This function creates a user so it can be used with the form that requires a user sign in
    Can take different usernames for testing different users 
    """
    CustomUser = get_user_model()
    self.user = CustomUser.objects.create_user(username=username, password="password123")
    self.client.login(username=username, password="password123") # Log the user in!

# test go here 
class ContentModelTests(TestCase):
    def test_no_duplicates(self):
        """
        this test makes sure that no duplicate words can be entered into the database
        """
        create_content("test case") # use function to create field in the db

        with self.assertRaises(IntegrityError):
            create_content("test case")

    def test_uppercase(self):
        """
        all entries in the dictionary should be lower case so it should refuse a similar entry even if the case is different
        """
        create_content("test case")

        # this will probably becuase the slug raises some errors
        with self.assertRaises(IntegrityError):
            create_content("TEST CASE") # this works because of slugify

    def test_entries_listed(self):
        """
        Test to see if there are entries listed on the list view, only those set to 'Published' are visible
        """
        entry = create_content("test entry")
        response = self.client.get(reverse("site_content:content-list"))
        self.assertNotContains(response, "test entry") # make sure the title is not in the list since it isn't 'Published

        # set the article to 'Published'
        entry.status = 'P'

        # save the entry
        entry.save()

        # check the list again
        response = self.client.get(reverse("site_content:content-list"))
        self.assertNotContains(response, "No stories yet.")
        self.assertContains(response, "test entry")

    def test_none_listed(self):
        """
        Test to see if no entries will be listed if there are none in the database
        """
        response = self.client.get(reverse("site_content:content-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No stories yet.")   

    def test_detail_page(self):
        """
        Test to see if are being placed on the detail page
        """
        test_entry = create_content("test entry")
        response = self.client.get(reverse("site_content:content-detail", kwargs={"slug": test_entry.slug})) # need to do all of this since the url has a slug
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test entry")

    # I can add tests for case and punctuation but I feel like that's okay for the titles to have

class DictionaryEntryUserTests(TestCase):
    """
    This test class is for all tests that require a user login 
    This class uses the built in setUpTestData() function to increase the speed of the tests
    """
    @classmethod
    def setUpTestData(cls):
        """
        Set up function that will be run automatically ONCE then all the tests are done
        Best from read-only data that can't be modified
        """
        # set up a basic user for all tests
        CustomUser = get_user_model()
        cls.user = CustomUser.objects.create_user(username="test_user", password="password123")

    def setUp(self):
            """
            This code is done before EVERY test 
            """
            # log the user in since it was getting messed up in setUpTestData
            self.client.login(username="test_user", password="password123") 
    
            return super().setUp()

    def test_update_view(self):
        """
        Test to see if update view changes the definition for a word
        Date modified should also changed 
        Publish date should not change
        """

        # test looking at the website page
        test_content = create_content("test") # test a word like ngombe using the past function so the date is in the past
        model_1 = Content.objects.get(title="test")
        last_modified_1 = model_1.last_modified
        pub_date_1 = model_1.pub_date
        response1 = self.client.get(reverse("site_content:content-detail", kwargs={"slug": test_content.slug})) # get the entry page
        self.assertEqual(response1.status_code, 200) # test to make sure it's populating

        # test if we enter new data 
        url = reverse("site_content:update-content", kwargs={"slug": test_content.slug}) # including reverse in the url
        form_data = create_content_form_data("test","test that this entry is different")

        # test we can open the update form page
        response2 = self.client.get((url))
        self.assertTemplateUsed(response2, "site_content/content_update_form.html")

        # post wasn't working because it was clearing the fields that are required 
        response3 = self.client.post(url, data = form_data)
        self.assertEqual(response3.status_code, 302) # 302 for redirect
        
        # test that the new text is on the entry page 
        response4 = self.client.get(reverse("site_content:content-detail", kwargs={"slug": test_content.slug}))
        self.assertContains(response4,'test that this entry is different')

        # test and make sure some stuff changed and other stuff didn't
        model_2 = Content.objects.get(title="test")
        last_modified_2 = model_2.last_modified # are objects not dictionaries so its just super easy to do this
        pub_date_2 = model_2.pub_date
        self.assertEqual(pub_date_1, pub_date_2)
        self.assertNotEqual(last_modified_2, last_modified_1)

    def test_if_no_modification(self):
        """
        Test to see if the form doesn't change user modified if nothing was changed in the form and it was just opened and entered
        """

        # test looking at the website page
        test_content =  create_content("test") # test a word like ngombe using the past function so the date is in the past

        # get url for the update entry page
        url = reverse("site_content:update-content", kwargs={"slug": test_content.slug}) # including reverse in the url

        # update with post 
        form_data = create_content_form_data("test","test basic")
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 302) # make sure it was redirected

        # get the new date modified 
        entry_1 = Content.objects.get(title="test")
        date_1 = entry_1.last_modified

        # update the same thing and nothing should change (including user and time modified)
        form_data = create_content_form_data("test","test basic")
        response_2 = self.client.post(url, data = form_data)
        self.assertEqual(response_2.status_code, 302)
        # get the new date modified 
        #time.sleep(0.1)
        entry_2 = Content.objects.get(title="test")
        date_2 = entry_2.last_modified
        # make sure both detail pages were the same
        self.assertEqual(date_1, date_2)

    def test_changing_entry_update_view(self):
        """
        This test checks to make sure that if an entry is updated it won't be added if its a duplicated of another entry that already exists
        This should work even if punctuation or uppercase values are added 

        """
        # have to log in a user for them to enter data with the form
        # create_user(self,"testuser")  <--- done in setUp()

        # test looking at the website page
        create_content("test") # make a entry that's to compare against
        test_content_2 = create_content("test_2")

        # get url for the update entry page
        url = reverse("site_content:update-content", kwargs={"slug": test_content_2.slug}) # including reverse in the url

        # update with post 
        form_data = create_content_form_data ("test","test basic") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

    def test_different_users(self):
        """
        Test to make sure that user modified is different for different users but the original user_added stays the same
        The "user_added" field should only be populated from the form since that will eventually be given to a buffer and 
        we don't want the admin always getting credit for the saves

        This tests the date modified and added as well just to be sure

        """

        # test looking at the website page
        test_content = create_content("test") # make a entry that's to compare against
        url = reverse("site_content:update-content", kwargs={"slug": test_content.slug}) # including reverse in the url
                
        # update with post to write the user 
        form_data = create_content_form_data("test","test basic") # have the form be denied since it matches the first word
        self.client.post(url, data=form_data) # post to the form 

        # add a user
        create_user(self,"testuser_2")
        
        # get url for the update entry page
        url = reverse("site_content:update-content", kwargs={"slug": test_content.slug}) # including reverse in the url

        # update with post 
        form_data = create_content_form_data("test","changed the content text") # have the form be denied since it matches the first word
        self.client.post(url, data=form_data) # post to the form 

        # refresh the entry from the database
        test_content.refresh_from_db()

        # no user modified in the database
        # # get the different users involved 
        # user_added = test_content.author
        # user_modified = test_entry.user_modified

        # # two items should be different
        # self.assertNotEqual(user_added,user_modified)

        # get the different users involved 
        date_added = test_content.pub_date
        date_modified = test_content.last_modified

        # two items should be different
        self.assertNotEqual(date_added,date_modified)

    def test_user_save(self):
        """
        This test makes sure that a basic save() doesn't add the user which may mess things up in the future

        """
        # create the first user
        #create_user(self,"testuser") <--- done in setUp()

        # test looking at the website page
        test_entry = create_content("test") # make a entry that's to compare against
        #self.assertEqual(test_entry.date_added, None) don't super care about date added that can be the date it gets confirmed by an admin
        self.assertEqual(test_entry.author, None)   

    # DELETE VIEW TEST
    def test_delete_view(self):
        """
        Test to see if the delete view works as expected
        """
        test_content = create_content("test") # test a word like ngombe using the past function so the date is in the past

        # get url for the update entry page
        url = reverse("site_content:delete-content", kwargs={"slug": test_content.slug}) # including reverse in the url

        # test that it opens the delete confirmation page
        response = self.client.get(url)
        self.assertContains(response, "Are you sure you want to delete")

        # test delete case using post
        response = self.client.post(url) # post to make sure it deletes
        self.assertEqual(response.status_code, 302) # should respond with 302 to redirect and delete the strings

        # make sure the entry no longer exists
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404) # need to use status code oops

    def test_adding_bad_values(self):
        """
        This test checks to make sure that if an entry will not be excepted if there are bad values in either "english" or the "swahili entry" fields
        Bad values include: spaces, punctuatin, single letter entries, or nothing at all

        """

        # test looking at the website page
        test_content = create_content("test") # make a entry that's to compare against

        # get url for the update entry page
        url = reverse("site_content:update-content", kwargs={"slug": test_content.slug}) # including reverse in the url

        # test single punctuation
        form_data = create_content_form_data("+","+") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

        # test single letter
        form_data = create_content_form_data("a","a") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

        # test spaces 
        form_data = create_content_form_data("   ","    ") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

        # test empty string
        form_data = create_content_form_data("","") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

        # test lots of punctuation
        form_data = create_content_form_data("+//...--","()>><>';;;") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

class DictionaryEntryAnonymousUserTests(TestCase):
    """
    Tests to be done if there is no user logged in
    """
    # TEST NUMBER 13
    def test_no_user_update_view(self):
        """
        This test checks to make sure that the form for dictionary view doesn't work if the user isn't logged in 
        """
    
         # test looking at the website page
        test_content = create_content("test") # make a entry that's to compare against

        # get url for the update entry page
        url = reverse("dictionary:update-entry", kwargs={"slug": test_content.slug}) # including reverse in the url

        # now the user can't even access the page
        response = self.client.get(url)

        # user will be automatically redirected
        self.assertEqual(response.status_code, 302) # <--- 302 for a redirect

    def test_no_user_update_view(self):
        """
        This test checks to make sure that the form for dictionary deleting of a word doesn't work if the user isn't logged in 
        """
    
        # test looking at the website page
        test_content = create_content("test") # make a entry that's to compare against

        # get url for the update entry page
        url = reverse("dictionary:delete-entry", kwargs={"slug": test_content.slug}) # including reverse in the url

        # now the user can't even access the page
        response = self.client.get(url)

        # user will be automatically redirected
        self.assertEqual(response.status_code, 302) # <--- 302 for a redirect

class ReaderViewTests(TestCase):
    """
    This class is for testing the reader view which will be a bit difficult to test since it is not as 
    easy to test the javacript part of the code
    Reader view also requires that content is added through the content tool so each word has a definition
    """
    def test_basic_view(self):
        """
        The reader view should be accessible once there an object is in the data base
        """
        test_object = create_content("test")
        url = reverse("site_content:reader-view", kwargs={"slug": test_object.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test")

    def test_fetch_database(self):
        """
        This tests makes sure the fetch call works if there is an entry in the dictionary db
        """
        test_entry = create_basic_entry("nitaenda")

        url = reverse("site_content:fetch-database-entry", kwargs={"word": test_entry.swahili_entry})
        
        # 2. Make a GET request to that URL using the built-in test client
        response = self.client.get(url)
        
        # 3. Assertions to verify the behavior
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/json")
        
        # 4. Check the JSON payload data
        json_data = response.json()
        self.assertEqual(json_data["english"], "default") # <-- basic value created by the create_entry function

    def test_fetch_blank_database(self):
            """
            This tests makes sure the fetch call returns an error if nothing is found in the database
            """
    
            url = reverse("site_content:fetch-database-entry", kwargs={"word": "test"})
            
            # 2. Make a GET request to that URL using the built-in test client
            response = self.client.get(url)
            
            # 3. Assertions to verify the behavior
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response["content-type"], "application/json")
            
            # 4. Check the JSON payload data
            json_data = response.json()
            self.assertEqual(json_data["success"], False) # make sure the function call was unsuccessful