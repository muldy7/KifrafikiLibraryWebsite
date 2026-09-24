from django.views.generic import ListView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Content
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ContentUpdateForm
from django.shortcuts import render
from django.http import JsonResponse
from dictionary.models import DictionaryEntry
 
 
class ContentListView(ListView):
    model = Content
    template_name = "site_content/content_list.html"
    context_object_name = "stories"
    ordering = ["-pub_date"]

    # make it so the list view only shows articles that are 'published'
    def get_queryset(self):
        return Content.objects.filter(status='P') # have to use the code that django uses oops haha
 
 
class ContentDetailView(DetailView):
    """Shows a single story, looked up by its slug."""
    model = Content # from the site_content model page
    template_name = "site_content/content_detail.html"
    context_object_name = "content" # this is then given to the template for it to use
    slug_field = "slug"        # the model field to match against, this makes a human readble url instead of just the pk
    slug_url_kwarg = "slug"    # the URL keyword argument name (must match urls.py below)

# more generic views for update and deleting content 
class ContentUpdateView(SuccessMessageMixin,LoginRequiredMixin,UpdateView): # success message has to go to the left
    model = Content
    form_class = ContentUpdateForm
    #fields = ["title", "content","level", "source"]
    template_name_suffix = "_update_form"
    success_message = "Content updated successfully"

    def get_success_url(self):
        # Extract the slug parameter from the current incoming URL
        current_url_slug = self.kwargs.get('slug') # get slug from what is stored currently in the url

        # find the link to return to after saving
        return reverse("site_content:content-detail", kwargs={"slug": current_url_slug}) # this isn't going backwards but it uses the url name in url.py
    
    # have some stuff happen automatically to the form
    # can do this even in class view
    def form_valid(self, form):
        # 1. Access the model instance attached to the form but don't commit to DB yet
        if form.has_changed():
            self.object = form.save(commit=False)
        
            # 2. Inject your automatic data changes
            self.object.last_modified = timezone.now() 
        
            # 3. Save the object to the database
            self.object.save()
        
        # 4. Trigger standard redirection
        return super().form_valid(form)

# delete view class from the django documentation
class ContentDeleteView(SuccessMessageMixin,DeleteView):
    model = Content
    success_url = reverse_lazy("site_content:content-list") # can't forget the app name
    success_message = "Entry deleted successfully" # this will get shown at the top of the list view


# view for making a reader view where we can click on the words
# going to keep this view seperate for now and just have it connect to the list view
def reader_view(request,slug): # <---- can give the view the slug and then it can look up the content!
    """
    This view uses a new template and javascript so each word in the text is clickable
    The clickable text then opens the side bar with the definiton of the word
    Reader view is a temporary name that will eventually replace the detail view
    """
    # get the object from the db
    content = Content.objects.get(slug=slug)

    # create the basic words by splitting at the spaces, this should keep punctuations
    # going to split the sentences into paragraphs since 
    #words = content.content.split()
    content_body = content.content # a little confusing since the name is the same haha
    paragraphs = content_body.split('\n\n')

    # create the structured content and set any '$' as one word
    structured_content = []
    for para in paragraphs:
        # split each paragraph into lines by single newlines
        lines = para.split('\n')
        para_lines = []
        for line in lines:
            # split lines into individual words
            words = line.split()
            line_words = []
            for word in words:
                #print(word)
                if "$" in word:
                    word = word.replace('$',' ') # have to set it equal otherwise it doesnt change
                    #print(word)
                line_words.append(word)
            para_lines.append(line_words)
        structured_content.append(para_lines)

    # create context for the view
    context = {
        "structured_content": structured_content,
        "author": content.author,
        "pub_date": content.pub_date,
        "title": content.title,
        "source": content.source,
        "last_modified": content.last_modified
               } # this is the context given to the website

    # i can give the view whatever I need in "context"
    return render(request, "site_content/reader_view.html", context)


def fetch_database_entry(response,word):
    """
    Called by the reader view via fetch, this function should grab the entries from the database and 
    give them to the side bar 
    """
    # convert all to lower case letters since that's how its stored in the dictionary
    word = word.lower()

    # get the word entry from the database
    try:
        # Try to find the entry in the database
        dict_entry = DictionaryEntry.objects.get(swahili_entry=word) 
        
        # If found, return the full entry data
        return JsonResponse({
            "success": True,
            "swahili_entry": dict_entry.swahili_entry,
            "english": dict_entry.english,
            "part_of_speech": dict_entry.part_of_speech,
            "construction": dict_entry.construction,
            "sentence": dict_entry.sentence,
            "translation_source": dict_entry.translation_source
        })
        
    except DictionaryEntry.DoesNotExist:
        # If not found, return a clean error message and a 404 status code
        return JsonResponse(
            {
                "success": False,
                "error": f"The word '{word}' was not found in the dictionary."
            }, 
            status=404
        )



