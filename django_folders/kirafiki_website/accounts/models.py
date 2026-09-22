#this is models.py in my accounts app for handling the different user logins
from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
# model for a user that I can change later if I need to
# there is a built-in model but it is reccomended to use this just incase I want to update it later
class CustomUser(AbstractUser):
    # I can add more stuff here if I want to

    def __str__(self):
        return self.username