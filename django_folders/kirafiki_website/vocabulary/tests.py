from django.test import TestCase
from dictionary.tests import create_basic_entry # need for create words to add to a user's list
from site_content.tests import create_content # need to add some content so we can test "added_from"
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import ListAddition, VocabularyList
from dictionary.models import DictionaryEntry
from django.contrib.messages import get_messages # to get error messages
# Create your tests here.
"""
TESTS TO MAKE:
1. if the user doesnt have a list it should make a new one (DONE)
2. cant add a word to the list if the user isnt logged in (DONE)
3. cant add a word that doesn't exist (DONE)
4. do something this for the add word: url = reverse("site_content:fetch-database-entry", kwargs={"word": "test"}) (DONE)
5. should not add a word that already is on the list to the list (DONE)
6. test if the definition changes on the list if we change the word (DONE)
7. delete a single word
8. delete the full list
""" 

"""
VOCABULAR LIST FUNCTIONS
"""
def create_user(self,username):
    """
    This function creates a user so it can be used with the form that requires a user sign in
    Can take different usernames for testing different users 
    """
    CustomUser = get_user_model()
    self.user = CustomUser.objects.create_user(username=username, password="password123")
    self.client.login(username=username, password="password123") # Log the user in!

"""
VOCABULARY LIST TESTS
"""
class VocabularyListNoUserTests(TestCase):
    def test_no_user_login(self):
        """
        The vocabulary list should not allow an addition to the list if the user is not logged in
        """
        create_basic_entry("test")
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "test"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # it should ask the user to login with a redirect
        
    def test_vocab_list(self):
        """
        The user should be asked to login if they try and access the vocab list without a login
        """
        url = reverse("vocabulary:my-vocab-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

class VocabularyListUserTests(TestCase):
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

    """
    TESTS
    """
    def test_user_no_list(self):
        """
        Test if a list is create if they try and access the site without a list
        """
        url = reverse("vocabulary:my-vocab-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your vocabulary list is empty. Start adding words!")
        self.assertTemplateUsed(response, "vocabulary/user_vocab_list.html")

    def test_word_doesnt_exist(self):
        """
        Test if a word refuses if it doesnt exist
        """
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "test"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # should redirect to home

        # get the error message
        storage = get_messages(response.wsgi_request)
        messages_list = list(storage)
        
        # check the message matches
        message = messages_list[0]
        # check the exact text
        self.assertEqual(message.message, "Error 'test' Not found in database.")

    def test_successful_save(self):
        """
        Test if a word can we saved to the vocab list as expected
        """
        create_basic_entry("test")
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "test"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # should be a 204 if successful

        # test if the word is on the list
        url = reverse("vocabulary:my-vocab-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test")

    def test_adding_word_twice(self):
        """
        Test if a word is refused if its already on the list
        """
        create_basic_entry("test")
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "test"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # should redirect to home

        # try adding the word again
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "test"})
        response = self.client.get(url)
        
        # get the error message
        storage = get_messages(response.wsgi_request)
        messages_list = list(storage)
        
        # check the message matches
        message = messages_list[1] # will be the second message in the list
        # check the exact text
        self.assertEqual(message.message, "Error 'test' Is already in your vocabulary list.")

    def test_translation_changes(self):
        """
        Test that a word on the list updates if the word is update elsewhere
        """
        test_entry = create_basic_entry("test")
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "test"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # should be a 204 if successful

        # test if the word is on the list
        url = reverse("vocabulary:my-vocab-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test")
        self.assertContains(response, "default") # the first definition
        

        # change the english translation
        test_entry.english = "This is an updated field"
        test_entry.save()

        # test to see if the list has been updated
        url = reverse("vocabulary:my-vocab-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is an updated field")

    def test_delete_list_addition(self):
        """
        Test to see if the delete a single list addiiton works
        """
        create_basic_entry("testing")
        test_word = create_basic_entry("another word")

        # add the first word
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "testing"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # should redirect to home

        # add the second word
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "another word"})
        response = self.client.get(url)

        # get the list addition
        test_list = VocabularyList.objects.get(owner=self.user)
        test_addition = ListAddition.objects.get(vocab_list= test_list, word = test_word.pk)

        # get url for the delete page using pk
        url = reverse("vocabulary:delete-word", kwargs={"pk": test_addition.pk}) # including reverse in the url

        # test that it opens the delete confirmation page
        response = self.client.get(url)
        self.assertContains(response, "Are you sure you want to delete")

        # test delete case using post
        response = self.client.post(url) # post to make sure it deletes
        self.assertEqual(response.status_code, 302) # should respond with 302 to redirect and delete the strings

        # make sure that "test" is still on the list
        url = reverse("vocabulary:my-vocab-list")
        response = self.client.get(url)
        self.assertContains(response, "testing")
        self.assertNotContains(response, "Your vocabulary list is empty. Start adding words!")

    def test_delete_entire_list(self):
        """
        Test to see if the delete the entire list works
        """
        create_basic_entry("testing")
        create_basic_entry("another word")

        # add the first word
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "testing"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # should redirect to home

        # add the second word
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "another word"})
        response = self.client.get(url)

        # get the list addition
        test_list = VocabularyList.objects.get(owner=self.user)

        # get url for the delete page using pk
        url = reverse("vocabulary:delete-list", kwargs={"pk": test_list.pk}) # including reverse in the url

        # test that it opens the delete confirmation page
        response = self.client.get(url)
        self.assertContains(response, "Are you sure you want to delete")

        # test delete case using post
        response = self.client.post(url) # post to make sure it deletes
        self.assertEqual(response.status_code, 302) # should respond with 302 to redirect and delete the strings

        # make sure that "test" is still on the list
        url = reverse("vocabulary:my-vocab-list")
        response = self.client.get(url)
        self.assertNotContains(response, "testing")
        self.assertContains(response, "Your vocabulary list is empty. Start adding words!")

    def test_different_user_lists(self):
        """
        Test to make sure if two different users have the same word on their list it won't be deleted
        from both lists,

        """
        test_entry = create_basic_entry("testing") # make a entry that's to compare against

        # add the first word
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": test_entry.swahili_entry})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # should redirect to home

        # store the current user
        user1 = self.user

        # add a user
        create_user(self,"testuser_2")

        # add the same word to the different user's list
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": test_entry.swahili_entry})
        response = self.client.get(url)

        # get the list addition
        test_list = VocabularyList.objects.get(owner=self.user)
        test_addition = ListAddition.objects.get(vocab_list= test_list, word = test_entry.pk)

        # get url for the delete page using pk
        url = reverse("vocabulary:delete-word", kwargs={"pk": test_addition.pk}) # including reverse in the url

        # test that it opens the delete confirmation page
        response = self.client.get(url)
        self.assertContains(response, "Are you sure you want to delete")

        # test delete case using post
        response = self.client.post(url) # post to make sure it deletes
        self.assertEqual(response.status_code, 302) # should respond with 302 to redirect and delete the strings

        # make sure that "test" is not on user 2's list
        url = reverse("vocabulary:my-vocab-list")
        response = self.client.get(url)

        # haha since the website now says "Karibu, test_user" it will cause this test to fail so I have to change the word
        self.assertNotContains(response, "testing")
        self.assertContains(response, "Your vocabulary list is empty. Start adding words!")

        # login original user
        self.client.login(username=user1, password="password123") 

        # make sure the word is still here
        url = reverse("vocabulary:my-vocab-list")
        response = self.client.get(url)
        self.assertContains(response, "test")
        self.assertNotContains(response, "Your vocabulary list is empty. Start adding words!")

    def test_added_from(self):
        """
        With the new "added_from" column, words added from the dictionary should say "added from dictionary" but words
        added from reader view should have a link to the content they came from.
        In this test we will mock the data that is grabbed from 'HTTP_REFERER'
        """
        # create entries to add to the list 
        create_basic_entry("test word")
        create_basic_entry("test 2")

        # add the first word to the list
        url = reverse("vocabulary:add-vocabulary-word", kwargs={"word": "test word"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302) # should redirect to home

        # check the list 
        list_url = reverse("vocabulary:my-vocab-list")
        response = self.client.get(list_url)
        self.assertContains(response, "Added from Dictionary")

        # make a content that we can pretend we're adding from
        test_content = create_content("test content")

        # make the urls
        fake_url = reverse("site_content:reader-view", kwargs={"slug": test_content.slug })
        add_word_url =  reverse("vocabulary:add-vocabulary-word", kwargs={"word": "test 2"})

        # added a second word this time pretending we're coming from reader view
        response = self.client.get(
            add_word_url, 
            HTTP_REFERER=fake_url
        )

        # check the list again
        response = self.client.get(list_url)
        self.assertContains(response, "test content")

    def test_highlight_url(self):
        """
        When "?highlight=" is added to the url it can cause problems. Make sure that the views detects the change and 
        it should still direct to the correct content from the vocabulary list. 
        """
        # create the entry 
        create_basic_entry("test word")

        # make a content that we can pretend we're adding from
        test_content = create_content("test content")

        # make the urls
        list_url = reverse("vocabulary:my-vocab-list")
        fake_url = reverse("site_content:reader-view", kwargs={"slug": test_content.slug })
        highlight_url = fake_url + "?highlight=test word"
        #print(highlight_url)
        add_word_url =  reverse("vocabulary:add-vocabulary-word", kwargs={"word": "test word"})

        # added a second word this time pretending we're coming from reader view
        response = self.client.get(
            add_word_url, 
            HTTP_REFERER=highlight_url
        )

        # check the list again
        response = self.client.get(list_url)
        self.assertContains(response, "test content")

# going to be a problem if a user adds a word from the dictionary and not reader view
"""
WORK PLAN:
1. make test for what is working (DONE)
2. add delete button and clickable link to the vocab list (DONE)
3. make vocab list button in the sidebar (DONE)
4. make an export to anki or csv button (DONE)
5. have fun!
6. only ask ai when im supeer stuck and have it look for issues instead of it just telling me what to do. I should understand
7. put stuff in the footer
8. add a simple css to the website
9. add a bug list and entry button to the core app
10. more tests
11. log in doesnt need to be there if theyve already logged in
12. need a create account page

"""
# need to add messages to the dictionary detail page
# also add thehtml stuff to the template
# Ill add a cute little alert to the screen if you click the add to dictionary button from the popup
# every word should be clickable to bring it to the dictionary entry page
# also we need a delete button don't we
# can just do that with the generic view
# can test what happens if a user gets deleted



# Let's build this well! take my time and have fun there is no rush!