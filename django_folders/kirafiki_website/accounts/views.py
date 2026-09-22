from django.shortcuts import render

# Create your views here.
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.contrib.messages.views import SuccessMessageMixin 

class SignUpView(SuccessMessageMixin,CreateView):
    """
    View for having a user create an account
    """
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "accounts/signup.html"
    success_message = "Account create successfully! Please sign in to continue."