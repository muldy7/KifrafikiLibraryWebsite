from django.db import models
from accounts.models import CustomUser
from django.utils.text import slugify
from django.conf import settings
import string


# Create your models here.
# I can add more defintions and functions to these since they're class based
class DictionaryEntry (models.Model):
    # dictionary fields
    # can add more later but I think that's enough for now
    swahili_entry = models.CharField(max_length=200, unique=True) # can change the name and length later, want unique entries for now, can have multiple definitions since that is way easier
    english = models.CharField(max_length=200)
    swahili_definition = models.TextField(blank=True, default="No Definition Listed") # this should be a definition is kiswahili
    sentence = models.TextField(blank=True, default="No Examples Listed") # might want to have a different default value here
    part_of_speech = models.CharField(max_length=200, blank=True, default="None Listed")
    construction = models.TextField(blank=True, max_length=500, default = "N/A") # for having entries that are ni + na + penda, but could also use with adjective and what not

    # date fields
    date_added = models.DateTimeField("Date Added")
    date_modified = models.DateTimeField("Date Last Modified")

    #user fields
    # should have the username in the text box
    user_added = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_added")
    user_modified = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_modified")

    # field for source from the translation 
    class TransSource(models.TextChoices):
          GOOGLE = 'GoogleTranslateAPI'    # what to choose incase it comes from a google translate API call
          FREE_DICT = 'FreeDictionaryAPI'    # free dictionary online api
          USER_ADDED = 'UserAdded'         # choose this if it was manually changed by a user
          #DEFAULT = 'D','No Source Found'      # think user added just makes this simplier

    # writing if the word was from a user manual entry or an api call
    translation_source = models.CharField(
        max_length=200,
        #choices=TransSource.choices, want to have custom entry too
        default=TransSource.USER_ADDED,
        )

    # have to add slug field for the word
    # slug field for better urls
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    # save the slug honestly not sure what is going on here but helpful for the website
    def save(self, *args, **kwargs):
        """
        what is done when the model is saved 
        """
        # eliminate all upper case characters the first time through
        if self.swahili_entry:
            clean = self.swahili_entry.strip(string.punctuation)
            self.swahili_entry = clean.lower() # lower doesn't change the value
            
        # make a slug from the entry
        if not self.slug:
            self.slug = slugify(self.swahili_entry)

        super().save(*args, **kwargs)

    def has_swahili_definition(self):
        if self.swahili_definition == "" or self.swahili_definition == "No definition listed":
            #print(self.swahili_definition)
            return False
        else:
            return True

    def __str__(self):
        return self.swahili_entry


# can add more stuff for the history of the entry and idk
# so funny that I actually have to use this damn Foreign Key, many-many stuff that I taught in Form3
    