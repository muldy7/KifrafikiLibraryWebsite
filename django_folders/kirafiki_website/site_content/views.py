from django.views.generic import ListView, DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from .models import Content
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ContentUpdateForm
 
 
class ContentListView(ListView):
    """Shows all stories, newest first."""
    model = Content
    template_name = "site_content/content_list.html"
    context_object_name = "stories"
    ordering = ["-pub_date"]
 
 
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
   

