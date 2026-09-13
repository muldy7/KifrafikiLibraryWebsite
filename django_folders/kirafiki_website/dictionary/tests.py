from django.test import TestCase
from .models import DictionaryEntry
from django.db.utils import IntegrityError
from django.utils import timezone
from django.urls import reverse
import datetime
from django.contrib.auth import get_user_model

# UNUSED IMPORTS
#from accounts.models import CustomUser
#import time

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
        "stage":"save_content" # have to include the stage since there is no redirect
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

    def test_content_tool_post(self):
        """
        Test if the content tool redirects to the add words page
        """
        url = reverse("dictionary:add-content")
        data_entry = create_content_form_data("test","test")

        # submit the form with the data entry
        response = self.client.post(url, data_entry) # <---- have to remeber the stage for the form to submit correctly that's nifty smart
        self.assertEqual(response.status_code, 200)  # <---- will post a 200 if the post works correctly
        self.assertContains(response, "Review Words")

        # make sure the new content wasn't yet added to the database
        with self.assertRaises(DictionaryEntry.DoesNotExist):
            DictionaryEntry.objects.get(swahili_entry='test')

        

        # testing this will be tricky because on the first stage we need to make sure the slug doesn't match, but I guess that won't be too hard
        # to test without saving I think I already figured that out didn't i
        # this testing is definitely teaching me how everything works damn those developers
        # it may be tricking while testing this because there is no redirect but we will see what happens

        # test to see if we're on the new page now
        #response = self.client.get(url)
        

        
        # will be a 200 if the post worls correctly
        # this is because its not a redirect but just changes the view which is good. 
        # A user can't go directly to the add words page


# add stuff for the delete views as well. 

# can add tests for the content entry form tooooooo ooff I'll make that as a new class though

# I'll add a Class here for the content submission tool. I can use the setUp() to make sure a user is automatically logged in
    # 1. I'll have to add one test above to make sure it can't be accessed without a user login (DONE)
    # 2. can test some stuff with the translation tool here too
    # 3. man this is a lot of work but so freaking awesome it's cool to see everything working well and know I have cracks filled
    # 4. lezyne really made me value doing a bunch of testing and i'm finding stuff
    # 5. punctuation can stay in the title but not the string so we'll have to take a look at just the slug and test that, if the strong is 
    #    different we'll make them look at a seperate title
    #    using login in the setUp but making in the user in create the test data seemed to serioulsy speed things up!
    #    lets try and do the basic test entry in test data next time but don't need to do anything now
    #    when a user presses the "add content tool" it should ask them to login, I should probably just do that to the update content button that's easier hmm

        # steps
        # add log in page
        # change forms I guess
        # okay I added a log in page and once I add "user required" it may mess some things up
        # the update and content user tool should be user only, so let's go make the changes to that


    