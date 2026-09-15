# IMPORTS
from django.views.generic import ListView, DetailView
from django.contrib.messages.views import SuccessMessageMixin # used for messages in class-based views
from .services import translate_word, letter_counter # from services.py file for the translate and letter_ count function
from .models import DictionaryEntry
from django.contrib.auth.mixins import LoginRequiredMixin
import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.contrib import messages
from site_content.models import Content
from .forms import DictionaryEntryForm, DictionaryUpdateForm
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy, reverse


 
 # views for the dictionary part of my website
class DictionaryListView(ListView):
    """shows all words, alphabetically."""
    model = DictionaryEntry
    template_name = "dictionary/dictionary_list.html"
    context_object_name = "dictionary_list"
    paginate_by = 25
    ordering = ["swahili_entry"] # order alphabetically 
 
# just copied this over from from views in site_content since it's super similar 
# this page REQUIRES LOGIN
class DictionaryDetailView(DetailView):
    """Shows a single word, looked up by its slug."""
    model = DictionaryEntry # from the site_content model page
    template_name = "dictionary/dictionary_detail.html"
    context_object_name = "word_entry" # this is then given to the template for it to use
    slug_field = "slug"        # the model field to match against, this makes a human readble url instead of just the pk
    slug_url_kwarg = "slug"    # the URL keyword argument name (must match urls.py below)

# these classes are still very customizable which is nice
# copied from the django documentation, this helps me change fields, would be easy to add a create button but think it's better to do that through the stories
class DictionaryUpdateView(SuccessMessageMixin,LoginRequiredMixin, UpdateView): # success message has to go to the left
    model = DictionaryEntry
    form_class = DictionaryUpdateForm
    #fields = ["swahili_entry", "english","part_of_speech", "swahili_definition","sentence", "construction", "translation_source"] no need since we are using form class
    template_name_suffix = "_update_form"
    success_message = "Entry updated successfully"

    def get_success_url(self):
        # Extract the slug parameter from the current incoming URL
        #current_url_slug = self.kwargs.get('slug') # get slug from what is stored currently in the url
        
        # don't need to use the current one since we're making a new slug and can just use that
        # find the link to return to after saving
        return reverse("dictionary:dictionary-detail", kwargs={"slug": self.object.slug}) # this isn't going backwards but it uses the url name in url.py
    
    # have some stuff happen automatically to the form
    # can do this even in class view
    def form_valid(self, form):
        # 1. Access the model instance attached to the form but don't commit to DB yet
        # this should hopefully take care of a user not changing anything
        if form.has_changed():
            self.object = form.save(commit=False)
        
        # 2. Inject your automatic data changes
            self.object.date_modified = timezone.now()
            self.object.user_modified = self.request.user # Example: Save who edited it, will be stored when we use the buffer

        # do this since in my model it's only done onthe first go
            self.object.slug = slugify(self.object.swahili_entry)

        #self.object.swahili_entry = self.object.swahili_entry.lower()
        #print(self.object.swahili_entry)
        # 3. Save the object to the database
            self.object.save()
        
        # 4. Trigger standard redirection
        return super().form_valid(form)


# delete view class from the django documentation
class DictionaryDeleteView(SuccessMessageMixin,LoginRequiredMixin,DeleteView):
    model = DictionaryEntry
    success_url = reverse_lazy("dictionary:dictionary-list") # can't forget the app name
    success_message = "Entry deleted successfully" # this will get shown at the top of the list view
    #messages.success("Dictionary Entry Deleted") this doesn't work since it needs the current http response

# FUNCTIONS FROM CLAUDE
# I should not trust these 100% and make sure I learn what is going on here 

def extract_unique_words(text):
    """
    Pulls every distinct word out of the story text, in the order each word
    first appears. 
    """
    #words = re.findall(r"[^\W\d_]+", text.lower()) # using regex to get rid of stuff in here 
    words = re.findall(r"[^\W\d_]+(?:['’][^\W\d_]+)*", text.lower()) # going to use this so it doesn't get rid of ng'ombe \W means not a word character
    seen = set()
    unique_words = [] # need a list of words that are new to the database
    for word in words:
        if word not in seen:
            seen.add(word)
            unique_words.append(word)
    return unique_words
 
 
@login_required # make it so a user needs to log in 
def add_content_view(request):
    """
    This view handles adding content to the website through a two-stage process
    Stage 1 is the "submit text" stage and handles the content itself and the title. This is connected to the Content model
    Stage 2 is connected to this dictionary and gives the user a table of the words in the content so they can add translations, etc

    characters_required sets the amount of characters a user must submit to have a valid story
    """
    # create the formset
    DictionaryEntryFormSet = modelformset_factory(DictionaryEntry, form=DictionaryEntryForm, extra=3)
 
    stage = request.POST.get("stage")
    characters_required = 5 # <----- this sets the amount of characters a user must enter when they write a story

    # SUBMIT TEXT STAGE OF THE VIEW
    if request.method == "POST" and stage == "submit_text":
        # ---- STEP 1: user just submitted the raw story text ----
        content_title = request.POST.get("content_title", "")
        content_body = request.POST.get("content_body", "")
        content_source = request.POST.get("content_source", "")
        content_level = request.POST.get("content_level", "")

        # going to count the character count of the fields
        letter_count = letter_counter(content_body)
        title_count = letter_counter(content_title)
        source_count = letter_counter(content_source)

        # make a count pass flag
        count_flag = 0 # flag to see if we pass both count tests

        # if the count is too low we should have them enter more words
        if letter_count < characters_required:
            messages.error(request, f"Error: Please write an entry of at least {characters_required} characters")
    
        # make sure that "title" isn't too short either
        elif title_count < 3: # <----- i can change this value later
            messages.error(request, f"Error: Please write a title of at least three characters")
        elif source_count < 3:
            messages.error(request, f"Error: Please write a source of at least three characters")
        else:
            count_flag = 1  # test passed with flying colors I LOVE FLAGS

        # test the pass flag
        if count_flag == 0:
            # go home!
            return render(request, "dictionary/add_content_text.html", { # refresh the view to enter the text again
                "content_title": content_title, 
                "content_body": content_body,
                "content_source": content_source,
                "content_level": content_level,
                })

    
        # need to test that the slug doesn't exist either if we slugify the title plus we shouldn't allow an empty content_level value
        test_slug = slugify(content_title)
        if Content.objects.filter(title = content_title).exists() or Content.objects.filter(slug=test_slug).exists() or content_level == "":
            # out put the message
            messages.error(request, f"Error '{content_title}' Title already exists.")

            # return with a fresh page
            return render(request, "dictionary/add_content_text.html", { # refresh the view to enter the text again
                #"formset": formset, # don't need formset on this step
                "content_title": content_title, 
                "content_body": content_body,
                "content_source": content_source,
                "content_level": content_level,
                })
        else:
            # do everything else
            # think I have to add a step here just in case it doesn't work
            unique_words = extract_unique_words(content_body)
    
            # Which of these words already exist in the dictionary?
            existing_entries = DictionaryEntry.objects.filter(swahili_entry__in=unique_words)
            existing_words = set(existing_entries.values_list("swahili_entry", flat=True)) # the string has to match field name in the model
    
            # Any word not already in the database needs a brand-new blank form.
            new_words = [w for w in unique_words if w not in existing_words]
    
            # Build a formset sized for exactly the new words we need to add,
            # on top of one form per existing word (from the queryset).
            FormSet = modelformset_factory(DictionaryEntry, form=DictionaryEntryForm, extra=len(new_words))
            formset = FormSet(
                queryset=existing_entries,
                initial=[{"swahili_entry": w} for w in new_words],
            )

            # would be good to add a field here so I can add the source and level
            # like not asking the AI for everything and then I have to figure stuff out 
            return render(request, "dictionary/add_content_words.html", { # where the view is using the template to render the html
                "formset": formset,
                "content_title": content_title, # like using content for now since maybe I'll have articles and other stuff in the future but people can help me with that 
                "content_body": content_body,
                "content_source": content_source,
                "content_level": content_level,
            })

    # SUBMIT WORDS TO THE DICTIONARY STAGE
    elif request.method == "POST" and stage == "save_content":
        # ---- STEP 2: user reviewed/edited the word table and hit final Save ----
        content_title = request.POST.get("content_title", "")
        content_body = request.POST.get("content_body", "")
        content_source = request.POST.get("content_source", "")
        content_level = request.POST.get("content_level", "")

        # going to check and make sure we can save here. Don't need to do a whole form or anything too complicated
        
        # Bind submitted data to the main FormSet template
        formset = DictionaryEntryFormSet(request.POST, queryset=DictionaryEntry.objects.all())
 
        if formset.is_valid():
            # Step A: Loop through the individual forms to attach meta user info
            for form in formset.forms:
                # Check if the form actually has data (skips empty extra forms)
                if form.has_changed():
                    # Extract the database instance object without saving it yet
                    entry = form.save(commit=False)

                    # Check if this specific entry is brand new (no primary key yet)
                    if entry.pk is None:
                        entry.user_added = request.user # since I have custom user this may fail later
                        entry.date_added = timezone.now()

                    # Apply updates to every entry being modified or added
                    entry.user_modified = request.user
                    entry.date_modified = timezone.now()

                    # Save this individual record to the database safely
                    entry.save()

            # Step B: Handle any items flagged for deletion safely outside the loop
            if formset.can_delete:
                formset.save(commit=False) 

            # Step C: Save the new story to the content database
            # okay maube since I called content earlier it got messed up
            new_content = Content(
                title=content_title,
                content=content_body,
                author=request.user,
                level=content_level,
                source=content_source,
                pub_date=timezone.now(),
                last_modified = timezone.now()
            )

            # save the new article
            new_content.save()

            # don't think this message is getting output?
            messages.success(request, "New content and dictionary words saved. Thank you!")
            #time.sleep(3) # maybe it's happening instantly or i just need to have a message pane on my other tab.
            # the message will never be posted so I'll have to fix that
            return redirect("site_content:content-list")  # adjust to your actual URL name
        # need an error if first step isn't valid
        else:
            # loop through errors if any pop-up on the second form page
            for form in formset: # have to loop through each form in the formset first 
                if form.errors:
                    # see whatever swahili word there is an error for (can add line number later)
                    swahili_entry = form.add_prefix('swahili_entry')
                    swahili_word = request.POST.get(swahili_entry, "Unknown Word")
                    for field, errors in form.errors.items(): # this has to be "formset" and not "forms"
                        for error in errors:
                        # going to get error and the field name for the error
                            messages.error(request, f"Error '{swahili_word}' ({field.title()}): {error}")
        # If the formset had errors, re-render step 2 with error messaging
        return render(request, "dictionary/add_content_words.html", {
            "formset": formset,
            "content_title": content_title,
            "content_body": content_body,
            "content_source": content_source,
            "content_level": content_level, # Fixed a typo from 'countent_level'
        })

    # if the form doesn't work do this last
    else: 
        formset = DictionaryEntryForm() # might need to change this since it's not a formset 


    # ---- Plain GET request: show the initial "paste your story" form ----
    return render(request, "dictionary/add_content_text.html",{'formset':formset})


# function from translating with my services function
def translate_suggestion(response, word):
    """
    Called by the per-row Translate button via fetch(). Returns a raw
    suggestion from the translation API WITHOUT saving anything to the
    database — the user can still edit the value before the final save.
    """

    # use my function to get a bunch of stuff from the API
    translated_text = translate_word(word) # this comes from the services.py file

    # what the api will output:
    # new_entry = {
    #         "swahili_entry": clean_text,
    #         "english": definition,
    #         "part_of_speech": part_of_speech,
    #         'construction': construction,
    #         #"date_added": timezone.now(), # i could also do this on the views side but might as well get it done now, not going to work since this isn't in django
    #         'sentence': example,
    #         'translation_source': source
    #     }
    # need to add stuff here so more stuff can come from the translate tool
    return JsonResponse(
        {"swahili_entry": translated_text["swahili_entry"],
         "english": translated_text["english"],
         "part_of_speech": translated_text["part_of_speech"],
         "construction": translated_text["construction"],
         "sentence": translated_text["sentence"],
         "translation_source": translated_text["translation_source"]
         })


# test code 
if __name__ == "__main__":
    title = Content(title = "TEST")