from django.db import models
from accounts.models import CustomUser

# Create your models here.
class BugReport(models.Model):
    """
    Class for a bug submission function on the website
    """
    title = models.CharField(max_length=200, unique=True, help_text="A short blurb about the bug you found") # field for a short bug summary
    submission_date = models.DateTimeField(auto_now_add=True) # added automatically
    summary = models.TextField(help_text="Please write a short summary of the bug you encountered")
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    # create a name for the object
    def __str__(self):
        return f"{self.title}"