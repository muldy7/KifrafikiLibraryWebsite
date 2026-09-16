from django.test import TestCase

# Create your tests here.
"""
TESTS TO MAKE:
1. if the user doesnt have a list it should make a new one
2. cant add a word to the list if the user isnt logged in
3. cant add a word that doesn't exist
4. do something this for the add word: url = reverse("site_content:fetch-database-entry", kwargs={"word": "test"})
5. should add a word that already is on the list to the list
"""

"""
WORK PLAN:
1. make test for what is working 
2. add delete button and clickable link to the vocab list
3. make vocab list button in the sidebar
4. make an export to anki or csv button
5. have fun!

"""
# need to add messages to the dictionary detail page
# also add thehtml stuff to the template
# Ill add a cute little alert to the screen if you click the add to dictionary button from the popup
# every word should be clickable to bring it to the dictionary entry page
# also we need a delete button don't we
# can just do that with the generic view
# can test what happens if a user gets deleted



# Let's build this well! take my time and have fun there is no rush!