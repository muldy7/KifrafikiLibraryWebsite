from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dictionary.models import DictionaryEntry
from .models import VocabularyList, ListAddition
from django.utils import timezone
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
# Create your views here.

# how to do values using through
# book = Book.objects.create(title="Django Guide")
# author = Author.objects.create(name="Jane Doe")

# # Record the relationship explicitly
# BookMembership.objects.create(
#     book=book, 
#     author=author, 
#     added_at=timezone.now()
# )

# # Get all memberships for a specific book, including author details
# memberships = BookMembership.objects.filter(book=book).select_related('author')

# for membership in memberships:
#     print(f"Author: {membership.author.name}")
#     print(f"Added at: {membership.added_at}")

# going to have a function to add words to the vocabulary list
# not sure how to do the anki export but maybe that can go in its own function
@login_required
def add_vocabulary_word(request,word):
    """
    This function will be used to add vocabulary words to a user's vocabulary list

    """
    # make sure the entry exists
    if DictionaryEntry.objects.filter(swahili_entry = word).exists():
        # find the word and create an entry for the current user 
        vocab_word = DictionaryEntry.objects.get(swahili_entry=word)

        # see if the user has a list already or not
        vocab_list, created = VocabularyList.objects.get_or_create(owner=request.user) # created is a False or True if it was created

        if ListAddition.objects.filter(vocab_list=vocab_list).select_related('word').exists(): # this returns true or false
            # add the word to the list if it doesn't already exist
            ListAddition.objects.create(
                    word = vocab_word, # this just takes the whole thing
                    vocab_list = vocab_list, 
                    added_at=timezone.now()
                    )
        else:
            # if the word is already in the list
            messages.error(request, f"Error '{word}' Is already in your vocabulary list.")
    else:
        messages.error(request, f"Error '{word}' Not found in database.")

        return redirect(reverse('core:home')) # just go home idk this is only for testing
    # have to end with a return
    return HttpResponse(status=204) # don't go anywhere but show we've had a success, this is good for later

# generic view for showing a user's vocabulary list
class UserVocabularyListView(LoginRequiredMixin, ListView):
    model = ListAddition
    template_name = 'vocabulary/user_vocab_list.html'
    context_object_name = 'vocab_entries'

    def get_queryset(self):
        # Automatically fetch the user's list, or safely create it if it doesn't exist
        vocab_list, created = VocabularyList.objects.get_or_create(owner=self.request.user)
        # not sure what to do with created here 
        # Now pull the entries for this specific list safely
        return (
            ListAddition.objects
            .filter(vocab_list=vocab_list)
            .select_related('word') # from the vocabulary model
            .order_by('-added_at') # sorting by words gets messed up if nothing is in the vocab list
        )