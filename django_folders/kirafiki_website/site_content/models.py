from django.db import models
from accounts.models import CustomUser

# Create your models here.
# model for the content hostedon the website that will include the text wrapping and all that

class Content(models.Model):
    title = models.CharField(max_length=200)
    pub_date = models.DateTimeField("Date Published")
    content = models.TextField(blank=True, null=True)

    # level field
    class Levels(models.TextChoices): # set the different levels the story can be, can change these later (using another class)
        BEGINNER = 'B', 'Beginner'
        INTERMEDIATE = 'I', 'Intermediate'
        ADVANCED = 'A', 'Advanced'
        LESSON = 'L', 'Lesson'
        NEWS = 'N', 'News'
        DEFAULT = 'D', 'Default' # set a default Level/category because I don't know what else to do

    # for setting the level of the stories "Beginner, Intermediate, Advanced"
    level = models.CharField(
        max_length=2,
        choices=Levels.choices,
        default=Levels.DEFAULT,
    )

    # copyright/data fields
    source = models.CharField(max_length=500) # for setting where the article may be sourced from through a link

    # set choice for status
    class Status(models.TextChoices): # set the different status the story can be (DRAFT OR PUBLISHED)
            PUBLISHED = 'P', 'Published'
            DRAFT = 'D', 'Draft'

    status = models.CharField(
            max_length=2,
            choices=Status.choices,
            default=Status.DRAFT,
        )

    # user fields
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="content_author")
    last_modified = models.DateTimeField("Last Modified")

    # add string so it's read easier
    def __str__(self):
        return self.title