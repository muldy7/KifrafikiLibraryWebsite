from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from dictionary.models import DictionaryEntry
from .models import VocabularyList, ListAddition
from django.utils import timezone
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.edit import UpdateView, DeleteView
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
    # save where the user was so we can go back there
    previous_url = request.META.get('HTTP_REFERER') 

    # make sure the entry exists
    if DictionaryEntry.objects.filter(swahili_entry = word).exists():
        # find the word and create an entry for the current user 
        vocab_word = DictionaryEntry.objects.get(swahili_entry=word)

        # see if the user has a list already or not
        vocab_list, created = VocabularyList.objects.get_or_create(owner=request.user) # created is a False or True if it was created

        if not ListAddition.objects.filter(vocab_list=vocab_list, word = vocab_word).exists(): # this returns true or false
            # add the word to the list if it doesn't already exist
            ListAddition.objects.create(
                    word = vocab_word, # this just takes the whole thing
                    vocab_list = vocab_list, 
                    added_at=timezone.now()
                    )
        else:
            # if the word is already in the list
            messages.error(request, f"Error '{word}' Is already in your vocabulary list.")

            return HttpResponseRedirect(previous_url)
    else:
        messages.error(request, f"Error '{word}' Not found in database.")

        return redirect('home/') # just go home idk this is only for testing
    # send a success message
    messages.success(request, f"Succes! '{word}' has been added to your vocabulary list.")
    # have to end with a return
    return HttpResponseRedirect(previous_url) # don't go anywhere but show we've had a success, this is good for later

# generic view for showing a user's vocabulary list
class UserVocabularyListView(LoginRequiredMixin, ListView):
    model = ListAddition
    template_name = 'vocabulary/user_vocab_list.html'
    context_object_name = 'vocab_entries'

    def get_queryset(self):
        # Automatically fetch the user's list, or safely create it if it doesn't exist
        vocab_list, created = VocabularyList.objects.get_or_create(owner=self.request.user)
        
        # Now pull the entries for this specific list safely
        return (
            ListAddition.objects
            .filter(vocab_list=vocab_list)
            .select_related('word') # from the vocabulary model
            .order_by('-added_at') # sorting by words gets messed up if nothing is in the vocab list
        )

# delete view class from the django documentation
# will delete with primary key
class ListAdditionDeleteView(SuccessMessageMixin,LoginRequiredMixin,DeleteView):
    model = ListAddition
    success_url = reverse_lazy("vocabulary:my-vocab-list") # can't forget the app name
    success_message = "Word deleted successfully" # this will get shown at the top of the list view


class VocabListDeleteView(SuccessMessageMixin,LoginRequiredMixin,DeleteView):
    """
    This view deletes the entire list and then goes back to the vocab page which should be empty, 
    but is technically a new list
    """
    model = VocabularyList
    success_url = reverse_lazy("vocabulary:my-vocab-list") # can't forget the app name
    success_message = "List cleared successfully" # this will get shown at the top of the list view


    """
    VIEWS TO ADD:
    1. delete one (DONE)
    2. clear list (DONE)
    3. export to csv
    4. export to anki
    """