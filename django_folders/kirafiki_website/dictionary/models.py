from django.db import models
from accounts.models import CustomUser


# Create your models here.
class DictionaryEntry (models.Model):
    # dictionary fields
    # can add more later but I think that's enough for now
    swahili_entry = models.CharField(max_length=200) # can change the name and length later
    english = models.CharField(max_length=200)
    swahili_definition = models.CharField(max_length=500,blank=True, default="No Definition Listed") # this should be a definition is kiswahili
    sentence = models.CharField(max_length=500, blank=True, default="No Examples Listed") # might want to have a different default value here
    part_of_speech = models.CharField(max_length=200, blank=True, default="None Listed")
    construction = models.CharField(max_length=500, default = "N/A") # for having entries that are ni + na + penda, but could also use with adjective and what not

    # date fields
    date_added = models.DateTimeField("Date Added")
    date_modified = models.DateTimeField("Date Last Modified")

    #user fields
    # should have the username in the text box
    user_added = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="entries_added")
    user_modified = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="entries_modified")

    def __str__(self):
            return self.swahili_entry


# can add more stuff for the history of the entry and idk
# so funny that I actually have to use this damn Foreign Key, many-many stuff that I taught in Form3
    