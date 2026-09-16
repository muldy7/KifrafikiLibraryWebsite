from django.test import TestCase
from .models import DictionaryEntry
from django.db.utils import IntegrityError
from django.utils import timezone
from django.urls import reverse
import datetime
from django.contrib.auth import get_user_model
from site_content.models import Content
from .services import lookup_word # for basic testing 

# functions to be used in tests
def create_basic_entry(test_entry):
    """
    Create a entry with the basic fields field with defaults since it will be the same fields every time
    The fields can be manually changed with the create function if needed 
    """
    # make the date_added in the past for testing 
    return DictionaryEntry.objects.create(swahili_entry= test_entry, english = "default", date_added = timezone.now(), date_modified=timezone.now())

def create_past_entry(test_entry):
    """
    Create a entry with the basic fields field with defaults since it will be the same fields every time
    The fields can be manually changed with the create function if needed 
    this function make an entry in the past for easier testing 
    """
    # make the date_added in the past for testing 
    return DictionaryEntry.objects.create(swahili_entry= test_entry, english = "default", date_added = timezone.now() + datetime.timedelta(days=-5), date_modified=timezone.now() + datetime.timedelta(days=-5))

def create_basic_form_data(test_entry, test_english):
    """
    This function creates a basic data field to be used to "POST" to a update form for testing
    The function needs to receive text for "english" and "swahili_entry
    """
    # can add things if more a required for the form 
    form_data = {
        "swahili_entry":test_entry,
        "english": test_english,
        "part_of_speech": "no part of speech",
        "swahili_definition": "no definition found",
        "sentence": "no sentence found", 
        "construction": "NULL", 
        "translation_source": "NULL"
    }

    return form_data

def create_content_form_data(title, content):
    """
    This function creates a data field to be used to "POST" to the content tool form for testing
    The function needs to receive text for "title" and "content"
    """
    # can add things if more a required for the form 
    form_data = {
        "content_title": title,
        "content_body": content,
        "content_level": "B",
        "content_source": "no source found",
        "stage":"submit_text" # have to include the stage since there is no redirect
    }

    return form_data

def formset_post_data(formset, rows, **extra):
    """
    This function creates a post data for the second stage of the content tool since it is required that 
    we retain the data from the first stage
    We need to do this function to deal with parts of the formset that are required for submission
    These are normally hidden to the user but required for testing
    """
    mf = formset.management_form
    data = {
        "form-TOTAL_FORMS": str(max(len(rows), mf.initial["TOTAL_FORMS"])),
        "form-INITIAL_FORMS": str(mf.initial["INITIAL_FORMS"]),
        "form-MIN_NUM_FORMS": "0",
        "form-MAX_NUM_FORMS": "1000",
    }
    for i, row in enumerate(rows):
        for name, value in row.items():
            data[f"form-{i}-{name}"] = value
        data.setdefault(f"form-{i}-id", "")
    data.update(extra)
    return data

def create_content(title,content):
    """
    This function acts as a way to create a basic entry into the Content model
    """
    return Content.objects.create(title= title, content = content, pub_date = timezone.now(), last_modified = timezone.now())

def create_user(self,username):
    """
    This function creates a user so it can be used with the form that requires a user sign in
    Can take different usernames for testing different users 
    """
    CustomUser = get_user_model()
    self.user = CustomUser.objects.create_user(username=username, password="password123")
    self.client.login(username=username, password="password123") # Log the user in!

# Create your tests here.
# I have to write test as the first word of the function or it wont be detected
# can walk through the tests in the shell or in the testing environment to make sure they're actually working
# a 200 status code from response.status_code means there's something at that url
# response.status_code will show 404 if there's nothing
# response.content shows the html code
# response = self.client.post(url, data=data) helps me put stuff in forms
# reverse just gets the full url from the url in the urls.py folder 

class DictionaryEntryModelTests(TestCase):
    # all test cases for my dictionaryentry model
    def test_has_swahili_definition(self):
        """
        Will test and return a True if it has a swahili definition

        (this is a basic testt to learn how to do them since they're very important for a strong website)
        """
        test_entry = DictionaryEntry.objects.create(swahili_entry='test case', swahili_definition='we are testing the definition', english = "", date_added = timezone.now(), date_modified=timezone.now())
        self.assertIs(test_entry.has_swahili_definition(), True)

    def test_no_duplicates(self):
        """
        this test makes sure that no duplicate words can be entered into the database
        """
        DictionaryEntry.objects.create(swahili_entry='test case', english = "", date_added = timezone.now(), date_modified=timezone.now()) # make a new entry with test case entry, all required fields

        with self.assertRaises(IntegrityError):
            DictionaryEntry.objects.create(swahili_entry='test case', english = "", date_added = timezone.now(), date_modified=timezone.now()) # make a new entry with test case entry, all required fields

    def test_uppercase(self):
        """
        all entries in the dictionary should be lower case so it should refuse a similar entry even if the case is different
        """
        DictionaryEntry.objects.create(swahili_entry='test case', english = "", date_added = timezone.now(), date_modified=timezone.now()) # make a new entry with test case entry, all required fields

        # this will probably becuase the slug raises some errors
        with self.assertRaises(IntegrityError):
            DictionaryEntry.objects.create(swahili_entry='TEST CASE', english = "", date_added = timezone.now(), date_modified=timezone.now()) # make a new entry with test case up case

    def test_entries_listed(self):
        """
        Test to see if there are entries listed on the list view
        """
        entry = create_basic_entry("test entry")
        response = self.client.get(reverse("dictionary:dictionary-list"))
        self.assertQuerySetEqual(response.context["dictionary_list"],[entry],)

    def test_none_listed(self):
        """
        Test to see if no entries will be listed if there are none in the database
        """
        response = self.client.get(reverse("dictionary:dictionary-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No entries yet.")

    def test_detail_page(self):
        """
        Test to see if are being placed on the detail page
        """
        test_entry = create_basic_entry("test entry")
        response = self.client.get(reverse("dictionary:dictionary-detail", kwargs={"slug": test_entry.slug})) # need to do all of this since the url has a slug
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test entry")

    def test_lowercase_conversion(self):
        """
        Test to see if uppercase entries are being converted to lower case
        """
        test_entry = create_basic_entry("TEST ENTRY")            
        response = self.client.get(reverse("dictionary:dictionary-detail", kwargs={"slug": test_entry.slug})) # need to do all of this since the url has a slug
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test entry")

    def test_punctuation_removed(self):
        """
        Test to see if punctuation is being removed from outside of the text but not the inside
        """
        test_entry = create_basic_entry("ng'ombe")
        response = self.client.get(reverse("dictionary:dictionary-detail", kwargs={"slug": test_entry.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ng&#x27;ombe") # all that &#x27; junk is how html stores an apostrophe safely
        with self.assertRaises(IntegrityError):
            create_basic_entry("?<>':ng'ombe;';") # this should still refuse a save
            create_basic_entry("ngombe") # this should still refuse a save since ngombe is the slug

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


    
    # for update view can test if date modified changes, if date added doesn't change, if date modified doesn't change
    # if nothing is changed, if a new entry is refused if there is a similar word with 
    # punctuation or upper case
    def test_update_view(self):
        """
        Test to see if update view changes the definition for a word
        Date modified should also changed 
        Publish date should not change
        """

        # test looking at the website page
        test_entry = create_past_entry("test") # test a word like ngombe using the past function so the date is in the past
        model_1 = DictionaryEntry.objects.get(swahili_entry="test")
        date_modified_1 = model_1.date_modified
        date_added_1 = model_1.date_added
        response1 = self.client.get(reverse("dictionary:dictionary-detail", kwargs={"slug": test_entry.slug})) # get the entry page
        self.assertEqual(response1.status_code, 200) # test to make sure it's populating

        # test if we enter new data 
        url = reverse("dictionary:update-entry", kwargs={"slug": test_entry.slug}) # including reverse in the url
        form_data = create_basic_form_data("test","test that this entry this different")

        # test we can open the update form page
        response2 = self.client.get((url))
        self.assertContains(response2,'Making changes to entry')

        # post wasn't working because it was clearing the fields that are required 
        response3 = self.client.post(url, data = form_data)
        #print(response3.context['form'].errors)
        self.assertEqual(response3.status_code, 302) # 302 for redirect
        
        # test that the new text is on the entry page 
        response4 = self.client.get(reverse("dictionary:dictionary-detail", kwargs={"slug": test_entry.slug}))
        self.assertContains(response4,'test that this entry this different')

        # test and make sure some stuff changed and other stuff didn't
        model_2 = DictionaryEntry.objects.get(swahili_entry="test")
        date_modified_2 = model_2.date_modified # are objects not dictionaries so its just super easy to do this
        date_added_2 = model_2.date_added
        self.assertEqual(date_added_1, date_added_2)
        self.assertNotEqual(date_modified_2, date_modified_1)

    # can add test to see if it refuses the different cases and what not
    def test_uppercase_and_punctuation(self):
        """
        Test to see if the form refuses an entry with the same word but different case or punctuation
        This should NOT be refused since the case and punctuation will be stripped automatically
        """
        # have to log in a user for them to enter data with the form
        # create_user(self,"testuser") <--- done in setUp()

        # test looking at the website page
        test_entry = create_past_entry("test") # test a word like ngombe using the past function so the date is in the past

        # get url for the update entry page
        url = reverse("dictionary:update-entry", kwargs={"slug": test_entry.slug}) # including reverse in the url

        # test upper case using post
        form_data = create_basic_form_data("tEst","test that different if case doesn't work")
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 302) # should respond with 302 to redirect and delete the strings
        
        # test that punctuation on the outside for similar words doesn't work either 
        form_data = create_basic_form_data("?/'test>-+","test that punctuation doesn't work")
        response_2 = self.client.post(url, data = form_data)
        self.assertEqual(response_2.status_code, 302)

        self.assertContains
        # text on the outside just get's fucked up but not much we can do about that

    # test to make sure it doesn't do stuff if there isn't a modification
    # this has to be indented correctly oof 
    # TEST NUMBER 11 <- check make to make sure the test is actually being read haha
    def test_if_no_modification(self):
        """
        Test to see if the form doesn't change user modified if nothing was changed in the form and it was just opened and entered
        """

        # test looking at the website page
        test_entry = create_past_entry("test") # test a word like ngombe using the past function so the date is in the past

        # get url for the update entry page
        url = reverse("dictionary:update-entry", kwargs={"slug": test_entry.slug}) # including reverse in the url

        # update with post 
        form_data = create_basic_form_data("test","test basic")
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 302) # make sure it was redirected

        # get the new date modified 
        entry_1 = DictionaryEntry.objects.get(swahili_entry="test")
        date_1 = entry_1.date_modified

        # update the same thing and nothing should change (including user and time modified)
        form_data = create_basic_form_data("test","test basic")
        response_2 = self.client.post(url, data = form_data)
        self.assertEqual(response_2.status_code, 302)
        # get the new date modified 
        #time.sleep(0.1)
        entry_2 = DictionaryEntry.objects.get(swahili_entry="test")
        date_2 = entry_2.date_modified

        # make sure both detail pages were the same
        self.assertEqual(date_1, date_2)

    # TEST NUMBER 12
    def test_changing_entry_update_view(self):
        """
        This test checks to make sure that if an entry is updated it won't be added if its a duplicated of another entry that already exists
        This should work even if punctuation or uppercase values are added 

        """
        # have to log in a user for them to enter data with the form
        # create_user(self,"testuser")  <--- done in setUp()

        # test looking at the website page
        create_past_entry("test") # make a entry that's to compare against
        test_entry_2 = create_past_entry("test_2")

        # get url for the update entry page
        url = reverse("dictionary:update-entry", kwargs={"slug": test_entry_2.slug}) # including reverse in the url

        # update with post 
        form_data = create_basic_form_data("test","test basic") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

    # TEST NUMBER 14
    def test_different_users(self):
        """
        Test to make sure that user modified is different for different users but the original user_added stays the same
        The "user_added" field should only be populated from the form since that will eventually be given to a buffer and 
        we don't want the admin always getting credit for the saves

        This tests the date modified and added as well just to be sure

        """
        # create the first user
        # create_user(self,"testuser")  <--- done in setUp()

        # test looking at the website page
        test_entry = create_past_entry("test") # make a entry that's to compare against
        url = reverse("dictionary:update-entry", kwargs={"slug": test_entry.slug}) # including reverse in the url
                
        # update with post to write the user 
        form_data = create_basic_form_data("test","test basic") # have the form be denied since it matches the first word
        self.client.post(url, data=form_data) # post to the form 

        # add a user
        create_user(self,"testuser_2")
        
        # get url for the update entry page
        url = reverse("dictionary:update-entry", kwargs={"slug": test_entry.slug}) # including reverse in the url

        # update with post 
        form_data = create_basic_form_data("test","changed the english description") # have the form be denied since it matches the first word
        self.client.post(url, data=form_data) # post to the form 

        # refresh the entry from the database
        test_entry.refresh_from_db()

        # get the different users involved 
        user_added = test_entry.user_added
        user_modified = test_entry.user_modified

        # two items should be different
        self.assertNotEqual(user_added,user_modified)

        # get the different users involved 
        date_added = test_entry.date_added
        date_modified = test_entry.date_modified

        # two items should be different
        self.assertNotEqual(date_added,date_modified)

    # TEST NUMBER 15
    def test_user_save(self):
        """
        This test makes sure that a basic save() doesn't add the user which may mess things up in the future

        """
        # create the first user
        #create_user(self,"testuser") <--- done in setUp()

        # test looking at the website page
        test_entry = create_past_entry("test") # make a entry that's to compare against
        #self.assertEqual(test_entry.date_added, None) don't super care about date added that can be the date it gets confirmed by an admin
        self.assertEqual(test_entry.user_added, None)   

    # DELETE VIEW TEST
    def test_delete_view(self):
        """
        Test to see if the delete view works as expected
        """
        test_entry = create_past_entry("test") # test a word like ngombe using the past function so the date is in the past

        # get url for the update entry page
        url = reverse("dictionary:delete-entry", kwargs={"slug": test_entry.slug}) # including reverse in the url

        # test that it opens the delete confirmation page
        response = self.client.get(url)
        self.assertContains(response, "Are you sure you want to delete")

        # test delete case using post
        response = self.client.post(url) # post to make sure it deletes
        self.assertEqual(response.status_code, 302) # should respond with 302 to redirect and delete the strings

        # make sure the entry no longer exists
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404) # need to use status code oops

    # TEST NUMBER 23 
    def test_adding_bad_values(self):
        """
        This test checks to make sure that if an entry will not be excepted if there are bad values in either "english" or the "swahili entry" fields
        Bad values include: spaces, punctuatin, single letter entries, or nothing at all

        """

        # test looking at the website page
        test_entry = create_past_entry("test") # make a entry that's to compare against

        # get url for the update entry page
        url = reverse("dictionary:update-entry", kwargs={"slug": test_entry.slug}) # including reverse in the url

        # test single punctuation
        form_data = create_basic_form_data("+","+") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

        # test single letter
        form_data = create_basic_form_data("a","a") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

        # test spaces 
        form_data = create_basic_form_data("   ","    ") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

        # test empty string
        form_data = create_basic_form_data("","") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied

        # test lots of punctuation
        form_data = create_basic_form_data("+//...--","()>><>';;;") # have the form be denied since it matches the first word
        response = self.client.post(url, data = form_data)
        self.assertEqual(response.status_code, 200) # make sure it was the change was denied


# NO USER TEST CLASS
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
        test_entry = create_past_entry("test") # make a entry that's to compare against

        # get url for the update entry page
        url = reverse("dictionary:update-entry", kwargs={"slug": test_entry.slug}) # including reverse in the url

        # now the user can't even access the page
        response = self.client.get(url)

        # user will be automatically redirected
        self.assertEqual(response.status_code, 302) # <--- 302 for a redirect

    def test_no_user_update_view(self):
        """
        This test checks to make sure that the form for dictionary deleting of a word doesn't work if the user isn't logged in 
        """
    
        # test looking at the website page
        test_entry = create_past_entry("test") # make a entry that's to compare against

        # get url for the update entry page
        url = reverse("dictionary:delete-entry", kwargs={"slug": test_entry.slug}) # including reverse in the url

        # now the user can't even access the page
        response = self.client.get(url)

        # user will be automatically redirected
        self.assertEqual(response.status_code, 302) # <--- 302 for a redirect

    # TEST NUMBER 17
    def test_content_tool_no_user(self):
        """
        This test ensures that the content tool cannot be used if a user is not logged in
        """

        # try accessing the website
        response = self.client.get(reverse("dictionary:add-content"))

        # user will be automatically redirected
        self.assertEqual(response.status_code, 302) # <--- 302 for a redirect


        # need to add two tests and see if it blocks a user from entering 
        # the content entry tool and the update view page if they aren't signed in 
        # they should be redirected
        # i'll also see if it breaks any of my tests. Wow tests are so cool!
        # need to test the delete page as well


# CONTENT ENTRY TOOL TEST CLASS
# python manage.py test dictionary.tests.ContentEntryToolTests
class ContentEntryToolTests(TestCase):
    """
    Test class for tests involving the content entry tool
    This content tool uses both the DictionaryEntry and Content models but the testing is done in this page
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

    # test content tool exists
    # TEST NUMBER 18
    def test_content_tool(self):
        """
        This is a basic initial test to make sure the content entry page can be accessed
        """
        # try accessing the website
        response = self.client.get(reverse("dictionary:add-content"))
        
        # user will should be sent to the website
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add New Content")
        self.assertNotContains(response, "No forms were generated by the server") # what will be said if there is an error and the forms fail to generate

    def test_content_tool_post(self):
        """
        Test if the content tool redirects to the add words page
        """
        url = reverse("dictionary:add-content")
        data_entry = create_content_form_data("test","test words") # <---- needs to be at least 5 words

        # submit the form with the data entry
        response = self.client.post(url, data_entry) # <---- have to remeber the stage for the form to submit correctly that's nifty smart
        self.assertEqual(response.status_code, 200)  # <---- will post a 200 if the post works correctly
        self.assertContains(response, "Review Words")

        # make sure the new content wasn't yet added to the database
        with self.assertRaises(Content.DoesNotExist):
            Content.objects.get(title='test')

    def test_content_tool_uppercase(self):
        """
        Test if the content tool allows titles that are the same but with uppercase
        The content tool should refuse the user from submitting the title 
        """
        create_content("test", "test words") # add a test entry to the Content data base

        url = reverse("dictionary:add-content")

        data_entry = create_content_form_data("TEST","test words") # try the same title but uppercase
        
        # submit the form with the data entry
        response = self.client.post(url, data_entry)
        self.assertEqual(response.status_code, 200)  # <---- will post a 200 if the post works correctly
        self.assertNotContains(response, "Review Words") # shouldn't get to the next stage if the title is the same
        
    def test_content_tool_no_content(self):
        """
        Test if the content tool allows a user to submit with nothing written
        """

        url = reverse("dictionary:add-content")

        data_entry = {
        "content_title": "test", # <--- submitting with title but no content 
        "content_level": "B",
        "stage":"submit_text" # have to include the stage since there is no redirect
        }

        
        # submit the form with the data entry
        response = self.client.post(url, data_entry)
        self.assertEqual(response.status_code, 200)  # <---- will post a 200 if the post works correctly
        self.assertNotContains(response, "Review Words") # shouldn't get to the next stage if the title is the same


    def test_content_tool_no_level_choice(self):
        """
        Test if the content tool allows a user to submit with no choice for "Level"
        """

        url = reverse("dictionary:add-content")

        data_entry = {
        "content_title": "test", # 
        "content_body": "test words",
        "stage":"submit_text" # have to include the stage since there is no redirect
        }

        # submit the form with the data entry
        response = self.client.post(url, data_entry)
        self.assertEqual(response.status_code, 200)  # <---- will post a 200 if the post works correctly
        self.assertNotContains(response, "Review Words") # shouldn't get to the next stage if there is no choice selection

    def test_content_tool_bad_values(self):
        """
        Test if the content tool allows a user to submit with bad values in the title or content body
        This include submissions of spaces, punctuation, or small entries
        """
        # create the url
        url = reverse("dictionary:add-content")

        # test submititng just spaces
        form_data = create_content_form_data("  ","  ")
        response = self.client.post(url, form_data)
        self.assertContains(response, "required") # beginning of the error message
        self.assertNotContains(response, "Review Words") # shouldn't get to the next stage if there is no choice selection

        # test submititng just empty strings
        form_data = create_content_form_data("","")
        response = self.client.post(url, form_data)
        self.assertContains(response, "Please write") # beginning of the error message
        self.assertNotContains(response, "Review Words") # shouldn't get to the next stage if there is no choice selection

        # test submititng one letter
        form_data = create_content_form_data("a","b")
        response = self.client.post(url, form_data)
        self.assertContains(response, "Please write") # beginning of the error message
        self.assertNotContains(response, "Review Words") # shouldn't get to the next stage if there is no choice selection

        # test submititng just spaces
        form_data = create_content_form_data("  ","  ")
        response = self.client.post(url, form_data)
        self.assertContains(response, "Please write") # beginning of the error message
        self.assertNotContains(response, "Review Words") # shouldn't get to the next stage if there is no choice selection

        # test submititng punctuation
        form_data = create_content_form_data("+_:><","./?'''")
        response = self.client.post(url, form_data)
        self.assertContains(response, "Please write") # beginning of the error message
        self.assertNotContains(response, "Review Words") # shouldn't get to the next stage if there is no choice selection

        # test submititng single punctuation
        form_data = create_content_form_data("?","%")
        response = self.client.post(url, form_data)
        self.assertContains(response, "Please write") # beginning of the error message
        self.assertNotContains(response, "Review Words") # shouldn't get to the next stage if there is no choice selection      

    # TEST NUMBER 25
    def test_translation_function(self):
        """
        This test performs a basic test of the translation tool function sinc ethe function of the button uses
        website based JavaScript and it can't be tested with python
        """
        #translated_word = lookup_word("sitaki") # using the translation function
        #self.assertIn("No examples found",translated_word)
        # I'll really have to understad how this button works if i want the edit button to work

    def test_two_stage_save(self):
        """
        This test performs a basic test of the add content tool and ensures that the new content is seen in the database
        
        """
        url = reverse("dictionary:add-content")
        # ---- stage 1 ----
        response_1 = self.client.post(url, {
            "stage": "submit_text",
            "content_title": "test",
            "content_body": "sitaki chakula",
            "content_source": "my head",
            "content_level": "B",      # must not be empty
        })
        self.assertEqual(response_1.status_code, 200)
        self.assertTemplateUsed(response_1, "dictionary/add_content_words.html") # cool I can test the template used with django
        self.assertFalse(Content.objects.filter(title="test").exists()) # the entry should not yet exist 

        formset = response_1.context["formset"] # save the formset from round one

        # ---- stage 2 ----
        # create a full row of data for the form 
        r1 = create_basic_form_data("sitaki","I don't want") # row 1
        r2 = create_basic_form_data("chakula","food") # row 2
         
        data = formset_post_data(
            formset,
            rows=[
                r1,
                r2,
            ],
            stage="save_content",   # include the same data from the first round
            content_title="test",
            content_body="sitaki chakula",
            content_source="my head",
            content_level="B",
            )
        
        response_2 = self.client.post(url, data)
        #self.assertContains(response_2, "blah balh ablha hahaha")
        self.assertEqual(response_2.status_code, 302)
        self.assertTrue(Content.objects.filter(title="test").exists())
        self.assertTrue(DictionaryEntry.objects.filter(swahili_entry="sitaki").exists())

    # TEST NUMBER 27
    def test_two_stage_bad_values(self):
        """
        This test performs a test of the content entry tool with different bad values
        
        """

        url = reverse("dictionary:add-content")

        # TEST #1 NO TITLE
        # ---- stage 1 ----
        response_1 = self.client.post(url, {
            "stage": "submit_text",
            "content_title": "",
            "content_body": "sitaki chakula",
            "content_source": "my head",
            "content_level": "B",      # must not be empty
        })

        self.assertEqual(response_1.status_code, 200) # <--- will always be a 200
        self.assertContains(response_1, "Please write a title of at least three characters")

        # with self.assertRaises(AssertionError):
        #     formset = response_1.context["formset"] # save the formset from round one

        # TEST TWO BAD VALUES
        # ---- stage 1 ----
        response_1 = self.client.post(url, {
            "stage": "submit_text",
            "content_title": "test",
            "content_body": "sitaki chakula",
            "content_source": "my head",
            "content_level": "B",      # must not be empty
        })

        # ---- stage 2 ----
        formset = response_1.context["formset"] # save the formset from round one

        # create a full row of data for the form 
        r1 = create_basic_form_data(" ","+++++") # row 1
        r2 = create_basic_form_data("c","   ") # row 2
         
        data = formset_post_data(
            formset,
            rows=[
                r1,
                r2,
            ],
            stage="save_content",   # include the same data from the first round
            content_title="test",
            content_body="sitaki chakula",
            content_source="my head",
            content_level="B",
        )
        response_2 = self.client.post(url, data)
        #self.assertContains(response_2, "blah balh ablha hahaha")
        self.assertEqual(response_2.status_code, 200) # should not redirect
        self.assertFalse(Content.objects.filter(title="test").exists())
        self.assertFalse(DictionaryEntry.objects.filter(swahili_entry="sitaki").exists())

    def test_existing_value(self):
        """
        This test ensures that when content is added words existing in the database are populated
        """
        url = reverse("dictionary:add-content")
        
        # 1. Setup the target pre-existing entry
        test_entry = create_basic_entry("sitaki")
        self.assertEqual(test_entry.english, "default") 

        # ---- STAGE 1: Submit Text ----
        response_1 = self.client.post(url, {
            "stage": "submit_text",
            "content_title": "test",
            "content_body": "sitaki chakula",
            "content_source": "my head",
            "content_level": "B",     
        })

        # Verify the view pulls the existing definition "default" to show the user
        self.assertContains(response_1, "default") 
        

    def test_partial_save(self):
        """
        This test ensures that when we save with the content tool it should bring us a partial save where some words are saved in the database
        but the full content itself is not saved.
        At same point I can change this to draft mode or something like that. Think it is easy enough to just write in seperate doc. 
        """

        url = reverse("dictionary:add-content")

        # TEST TWO BAD VALUES
        # ---- stage 1 ----
        response_1 = self.client.post(url, {
            "stage": "submit_text",
            "content_title": "test",
            "content_body": "sitaki chakula",
            "content_source": "my head",
            "content_level": "B",     
        })

        # ---- stage 2 ----
        formset = response_1.context["formset"] # save the formset from round one

        # create a full row of data for the form 
        r1 = create_basic_form_data("sitaki","new english definition") # row 1
        r2 = create_basic_form_data("chakula", "") # save a bad value for chakula
         
        data = formset_post_data(
            formset,
            rows=[
                r1,
                r2,
            ],
            stage="save_content",   # include the same data from the first round
            content_title="test",
            content_body="sitaki chakula",
            content_source="my head",
            content_level="B",
        )

        response_2 = self.client.post(url, data) # post to the second stage of the view
       
        self.assertEqual(response_2.status_code, 200) # should not redirect
        self.assertFalse(Content.objects.filter(title="test").exists()) # this shouldnt save
        self.assertFalse(DictionaryEntry.objects.filter(swahili_entry="chakula").exists()) # this as well
        self.assertTrue(DictionaryEntry.objects.filter(swahili_entry="sitaki").exists()) # sitaki should be valid and save

    def test_definition_changes(self):
        """
        This test ensures that when we change an existing entry in the content entry form 
        it safely updates the definition of that entry in the database.
        """
        url = reverse("dictionary:add-content")
        
        # 1. Setup the pre-existing entry
        test_entry = create_basic_entry("sitaki")
        self.assertEqual(test_entry.english, "default") 

        # ---- STAGE 1: Submit Text ----
        response_1 = self.client.post(url, {
            "stage": "submit_text",
            "content_title": "test",
            "content_body": "sitaki chakula",
            "content_source": "my head",
            "content_level": "B",     
        })

        # Verify the view pulls the existing definition "default" to show the user
        self.assertContains(response_1, "default") 
        
        # Pull the live formset instance rendered by the view
        formset = response_1.context["formset"] 

        # ---- STAGE 2: Edit & Submit Words ----
        # Rule 1: We must map the fields to match the exact keys returned by create_basic_form_data helper.
        r1 = create_basic_form_data("sitaki", "new updated english definition") 
        # CRITICAL FIX: Pass the actual ID of the pre-existing record so Django knows to edit, not create!
        r1["id"] = str(test_entry.id) 

        r2 = create_basic_form_data("chakula", "new english definition")
        # For a brand new word like chakula, the ID can remain empty
         
        # Bundle both rows safely along with the management variables
        data = formset_post_data(
            formset,
            rows=[r1, r2],  # MUST include both rows so formset_post_data matches TOTAL_FORMS counts
            stage="save_content",   
            content_title="test",
            content_body="sitaki chakula",
            content_source="my head",
            content_level="B",
        )

        # Post to the step-2 view processor execution loop
        response_2 = self.client.post(url, data) 

        # Assert a successful save execution redirected the user (302)
        self.assertEqual(response_2.status_code, 302) 
        
        # Verify the main tracking models saved cleanly
        self.assertTrue(Content.objects.filter(title="test").exists())
        self.assertTrue(DictionaryEntry.objects.filter(swahili_entry="chakula").exists())
        
        # 2. REFRESH FROM DB: Force Python to re-read the entry from the database 
        test_entry.refresh_from_db() 
        
        # 3. FINAL VERIFICATION: Check that the definition was successfully altered!
        self.assertEqual(test_entry.english, "new updated english definition")

    def test_compound_phrase(self):
        """
        This test is to see that if words are combined with the "$" they will be allowed in the content entry tool
        """
        url = reverse("dictionary:add-content")
        
        # ---- STAGE 1: Submit Text ----
        response_1 = self.client.post(url, {
            "stage": "submit_text",
            "content_title": "test",
            "content_body": "alikuwa$akiandika",
            "content_source": "my head",
            "content_level": "B",     
        })

        # make sure that the reponse contains the phrase without a space
        self.assertContains(response_1, "alikuwa akiandika") 

        
        

# can make a test to make sure the definition changes if we change it
# I might want to add a "add new word" later but I think if I do a huge upload it will be okay
# I can clean up this code later but honestly if it works. Might be good to look at it with fresh eyes to see how it's working. 
# test if some have errors and some dont it should save the good ones but not the full content. 
## ADD TEST AS I WRITE CODE, KEEP IT NICE AND EASY!!


    