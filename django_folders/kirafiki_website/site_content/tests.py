from django.test import TestCase
from .models import Content, Lesson
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

def create_content_with_body(title, body):
    """
    This function creates a basic content entry to the database if you want to write the body as well

    """
    return Content.objects.create(
        title= title, 
        content=body, 
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

    def test_dollar_sign_detail_view(self):
            """
            Test to see if the dollar sign is removed if used to combine words.
            If a dollar sign is used to combin words it will be stored in the database so it is sent to reader view 
            as one word but it shouldn't be shown to the user. It will be seen in the detail view for now. 
            """
            test_entry = create_content_with_body("test entry","dollar$sign")
            response = self.client.get(reverse("site_content:content-detail", kwargs={"slug": test_entry.slug}))
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "dollar sign")
    

class ContentUserTests(TestCase):
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
        Test to see if the delete view works as expected. 
        The delete view should also delete a lesson as well if it was added to the content.
        """
        test_content = create_content("test") # test a word like ngombe using the past function so the date is in the past

        # create a lesson to see if it deletes as well
        test_lesson = Lesson.objects.create(content=test_content,body="test body",last_edit=timezone.now())

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

        # make sure the lesson doesn't exist as well
        lesson_url = reverse("site_content:lesson-detail", kwargs={"slug": test_lesson.slug})
        
        # the user should be able to view 
        lesson_response = self.client.get(lesson_url)
        
        # user will shown the lesson page
        self.assertEqual(lesson_response.status_code, 404)
        self.assertFalse(Lesson.objects.filter(slug=test_lesson.slug).exists())

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

    def test_adding_lesson_successful(self):
        """
        Test a successful addition of a lesson
        """
        test_content = create_content("test") # make a entry that's to compare against

        # see if the original reponse says "Add a Lesson" in reader view
        content_url = reverse("site_content:reader-view", kwargs={"slug": test_content.slug})
        rv_response = self.client.get(content_url)

        # test for "Add a Lesson"
        self.assertContains(rv_response, "Add a Lesson")

        # get url for the add a lesson page
        url = reverse("site_content:add-a-lesson", kwargs={"slug": test_content.slug}) # including reverse in the url
        
        # the lesson is just added with what is written in the body and everything else comes from the slug (which should be unique)
        form_data = {
            "body": "test body"
        }

        # add a lesson
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 302) 

        # see if the new reponse says "View Lesson"
        content_url = reverse("site_content:reader-view", kwargs={"slug": test_content.slug})
        rv_response = self.client.get(content_url)

        # test for "View Lesson"
        self.assertContains(rv_response, "View Lesson")

        # test the lesson detail
        self.assertTrue(Lesson.objects.filter(body="test body").exists())

    def test_adding_lesson_twice(self):
        """
        If a lesson is already added for a certain content we shouldnt be able to add it again. 
        """
        test_content = create_content("test") # make a entry that's to compare against

        # get url for the add a lesson page
        url = reverse("site_content:add-a-lesson", kwargs={"slug": test_content.slug}) # including reverse in the url
        
        # the lesson is just added with what is written in the body and everything else comes from the slug (which should be unique)
        form_data = {
            "body": "test body"
        }

        # add a lesson
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 302) 

        # add a second lesson
        # the lesson is just added with what is written in the body and everything else comes from the slug (which should be unique)
        form_data = {
            "body": "test number 2"
        }

        # add a lesson
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # should not allow the form to be submitted
        self.assertContains(response, "A lesson for this content already exists. Please go back.")

        # test the lesson detail
        self.assertTrue(Lesson.objects.filter(body="test body").exists())

    def test_lesson_update(self):
        """
        Test to make sure the update lesson works as expected
        """
        test_content = create_content("test") # make a entry that's to compare against
        
        # get url for the add a lesson page
        url = reverse("site_content:add-a-lesson", kwargs={"slug": test_content.slug}) # including reverse in the url
        
        # the lesson is just added with what is written in the body and everything else comes from the slug (which should be unique)
        form_data = {
            "body": "test body"
        }

        # add a lesson
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 302) 

        # update the lesson
        # the lesson is just added with what is written in the body and everything else comes from the slug (which should be unique)
        form_data = {
            "body": "test number 2"
        }

        # get url for "update lesson"
        update_url = reverse("site_content:update-lesson", kwargs={"slug": test_content.slug}) # the slug is the same which I think is okay?

        # add a lesson
        response = self.client.post(update_url, data = form_data)
        self.assertEqual(response.status_code, 302) 

        # test the new lesson detail
        self.assertFalse(Lesson.objects.filter(body="test body").exists()) # should not exist
        detail_url = reverse("site_content:lesson-detail", kwargs={"slug": test_content.slug})
        detail_response = self.client.get(detail_url)
        self.assertContains(detail_response, "test number 2")

    def test_lesson_update_bad_values(self):
        """
        Test to make sure the update lesson won't allow bad values
        """
        test_content = create_content("test") # make a entry that's to compare against
        
        # get url for the add a lesson page
        url = reverse("site_content:add-a-lesson", kwargs={"slug": test_content.slug}) # including reverse in the url
        
        # the lesson is just added with what is written in the body and everything else comes from the slug (which should be unique)
        # try with a blank value
        form_data = {
            "body": ""
        }

        # the post should be refused
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) 

        #  try with just spaces
        form_data = {
            "body": "   "
        }

         # this should be refused too
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) 

        #  try just one character
        form_data = {
            "body": "a"
        }

        # this should be refused too
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) 

        # with a lot of punctuation
        form_data = {
            "body": "?><:''"
        }

        # this should be refused too
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) 


    def test_duplicate_slugs(self):
        """
        Test that content on the website won't have duplicate slugs.
        I think this is like super basic because unique = True but just have to be careful.
        """
        test_content = create_content("test")

        with self.assertRaises(IntegrityError):
            test_content_2 = create_content("test?")

        

class ContentAnonymousUserTests(TestCase):
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

    def test_lesson_update_view_no_login(self): 
        """
        A user should not be allowed to add or edit a lesson if they aren't logged into the website
        """
        test_content = create_content("test_content")

        # get url for the update entry page
        url = reverse("site_content:add-a-lesson", kwargs={"slug": test_content.slug}) # including reverse in the url

        # now the user can't even access the page
        response = self.client.get(url)

        # user will be automatically redirected
        self.assertEqual(response.status_code, 302)

        # if we add a lesson it still shouldn't work
        test_lesson = Lesson.objects.create(content=test_content,body="test body",last_edit=timezone.now())

        # url for viewing the lesson
        url = reverse("site_content:lesson-detail", kwargs={"slug": test_lesson.slug})

        # the user should be able to view 
        response = self.client.get(url)

        # user will shown the lesson page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test body")

        # user shouldn't be able to view the lesson 
        # url for viewing the lesson
        url = reverse("site_content:update-lesson", kwargs={"slug": test_lesson.slug})

        # the user should NOT be able to view 
        response = self.client.get(url)

        # user will shown the lesson page
        self.assertEqual(response.status_code, 302)
        #self.assertContains(response, "login")


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

    def test_dollar_sign_detail_view(self):
        """
        Test to see if the dollar sign is removed if used to combine words.
        If a dollar sign is used to combin words it will be stored in the database so it is sent to reader view 
        as one word but it shouldn't be shown to the user. 
        """
        test_entry = create_content_with_body("test entry","dollar$sign")
        response = self.client.get(reverse("site_content:reader-view", kwargs={"slug": test_entry.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dollar sign")


"""
TEST TO DO:
1. The lesson add might break if you try and add a lesson to a content that already has one idk, add view overwrites the existing lesson (DONE)
2. deleting the content should delete the lesson (TRUE)
3. if a word is deleted from the dictionary does it break reader view? (NO)
4. test if update lesson works (DONE)
"""