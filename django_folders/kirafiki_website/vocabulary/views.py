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
import csv
import io
import genanki
from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET
from .services import create_note,create_deck, make_model # from services.py to make the anki deck
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

        # add a 404 error if I want? idk
        #raise Http404("Question does not exist")
        return redirect(reverse_lazy('home')) # just go home idk this is only for testing
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


@require_GET
def export_anki_deck(request):
    """
    This view is to be used with a button in the vocabulary page to export a anki deck 
    from the user's vocabulary list
    """
    # create the notes 
    model = make_model()

    # get the user's list
    vocab_list = VocabularyList.objects.get(owner=request.user)

    # get all the words from the list as django objects
    vocab_words = ListAddition.objects.filter(vocab_list=vocab_list)

    # create a note list to add to
    note_list = []
    # loop through the words in the list
    for addition in vocab_words:
        word = addition.word
        entry = DictionaryEntry.objects.get(swahili_entry=word)
        note = create_note(model=model,swahili=entry.swahili_entry,english=entry.english,example=entry.sentence)
        note_list.append(note)

    # create a deck with the note list
    deck = create_deck(note_list)

    # make a buffer to put the file
    anki_buffer = io.BytesIO()

    # package the list 
    package = genanki.Package(deck)

    # write the package to a file in a buffer
    package.write_to_file(anki_buffer)

    # start from the beginning of the stream
    anki_buffer.seek(0)

    # create the file response
    response = FileResponse(
        anki_buffer, 
        as_attachment=True, 
        filename='kirafiki_vocabulary.apkg',
        content_type='application/apkg'
    )
    
    return response

@require_GET
def export_to_csv(request):
    """
    This view is for taking the user's vocabulary list and exporting it to a csv
    from there the user can export it to google sheets or whatever they want.
    """
    vocab_list = VocabularyList.objects.get(owner=request.user)
    
    # get all the words from the list as django objects
    vocab_words = ListAddition.objects.filter(vocab_list=vocab_list)
    
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="kirafiki_vocabulary.csv"'},
    )

    # create the basic file
    writer = csv.writer(response)
    writer.writerow(["Swahili Word", "English Translation", "Part of Speech", "Swahili Definition", "Examples", "Construction"])

    # add each word to the .csv
    for addition in vocab_words:
        word = addition.word
        entry = DictionaryEntry.objects.get(swahili_entry=word)
        writer.writerow([entry.swahili_entry, entry.english, entry.part_of_speech, entry.swahili_definition, entry.sentence, entry.construction])

    return response

"""
VIEWS TO ADD:
1. delete one (DONE)
2. clear list (DONE)
3. export to csv (DONE)
4. export to anki (DONE)
5. css for the anki is weird?
6. the add to vocab list gets messed up if there is a capital (DONE)
7. can customize the look of the anki decks
8. water.css looks so freaking sick!!!!!!
9. lets do the rest once I'm well rested and have fun with it lets go!
10. create and account view
"""