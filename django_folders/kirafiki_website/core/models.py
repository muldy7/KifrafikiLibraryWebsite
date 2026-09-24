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

    # choice for severity level and if the bug has been completed yet
    # these will be added later by admin
    class Severity(models.TextChoices): # set the different levels the story can be, can change these later (using another class)
            CRITICAL = 'C', 'Critical'
            MAJOR = 'M', 'Major'
            MINOR = 'T', 'Minor'    # t for tiny
            UNREVIEWED = 'D', 'Unreviewed'  # do for default
    
    # for setting the level of the stories "Beginner, Intermediate, Advanced"
    severity = models.CharField(
        max_length=2,
        choices= Severity.choices,
        default= Severity.UNREVIEWED,
    )

    class Status(models.TextChoices):
        REVIEW = 'R', 'Needs Review'
        PROGRESS = 'P', 'In Progress'
        FIXED = 'F', 'Bug Fixed'

    status = models.CharField(
        max_length=2,
        choices= Status.choices,
        default= Status.REVIEW,
    )

    # more notes for fixing the bugs
    notes = models.TextField(help_text="Any notes on what is causing the bug/solutions after fixing", blank=True, null=True)

    # set a field for relating this bug to other bugs
    related_bugs = models.ManyToManyField('self', blank=True, symmetrical=False)

    # create a name for the object
    def __str__(self):
        return f"{self.title}"