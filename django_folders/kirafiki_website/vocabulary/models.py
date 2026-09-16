from django.db import models
from dictionary.models import DictionaryEntry
from accounts.models import CustomUser
from django.utils.text import slugify
from django.utils import timezone

# going to Keep It Simple Stupid and not try too hard here 
# Create your models here.

# I think if I sort stuff alphabetically would be okay but i think 
# having the ability to know the content that the word came from and the 
# date added will be nice

# build good bones!

class VocabularyList (models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, unique=True, related_name="user_owner")
    vocab_words = models.ManyToManyField(DictionaryEntry, through='ListAddition',related_name='words')

    def save(self, *args, **kwargs):
        """
        what is done when the model is saved 
        """
        # don't know if I need this since each user has their own vocab list
        # # make a slug from the entry
        # if not self.slug:
        #     self.slug = slugify(self.owner) # each user get's their own list

        super().save(*args, **kwargs)

# vocab words will be added with these other additions beyond what is coming from the Dictionary Entry
class ListAddition(models.Model):
    vocab_list = models.ForeignKey(VocabularyList, on_delete=models.CASCADE)
    word = models.ForeignKey(DictionaryEntry, on_delete=models.CASCADE)
    # This field records when the connection was made
    added_at = models.DateTimeField(default=timezone.now) # this will not when the vocab word is added

# at some point I can add the article this came from so it can link back to that

# I can make sure they have a vocabulary list when they make an account