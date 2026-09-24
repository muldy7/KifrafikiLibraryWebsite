from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin 
from .models import BugReport
from django.urls import reverse_lazy, reverse
from .forms import BugReportForm


# simple views for different parts of my core website like about and home
# honestly in this app I could add a model for like version number and basic app stuff like that for future use
# if something doesn't have a home it can go in core
# these guys are lower case since they are functions

def about_view(request):
    # can add more stuff here later if I want to
    context = {
        'project_name': 'The Kirafiki Library',
        'version_num': '0.1.1'
    }
    return render(request, 'core/about.html', context)

def home_view(request):

    context = {
        'project_name': 'The Kirafiki Library',
        'version_num': '0.1.1'
    }
    return render(request, 'core/home.html', context)

class SubmitABug(SuccessMessageMixin,LoginRequiredMixin, CreateView):
    """
    Generic view for uploading a bug report to the website, this will just be viewed in the admin panel
    """
    model = BugReport

    # use a form for submitting the report
    form_class = BugReportForm
    success_message = "Bug submitted successfully. Thank you!"
    template_name = "core/create_a_bug.html"

    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        # Set the user field of the model instance to the currently logged-in user
        form.instance.author = self.request.user
        
        # Call the parent class form_valid method to save the object and redirect
        return super().form_valid(form)