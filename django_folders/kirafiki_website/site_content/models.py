from django.db import models
from accounts.models import CustomUser
from django.utils.text import slugify

# Create your models here.
# model for the content hosted on the website that will include the text wrapping and all that

class Content(models.Model):
    title = models.CharField(max_length=200, unique=True)
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
    source = models.CharField(max_length=500,default="No source found") # for setting where the article may be sourced from through a link

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
    #slug = models.SlugField(max_length=200, unique=True, default =  )  # for setting a name for the url
    last_modified = models.DateTimeField("Last Modified")

    # slug field for better urls
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    # ue slugify to make a nice url out of the title
    def save(self, *args, **kwargs):
        if not self.slug:
            # Convert "Hello World!" -> "hello-world"
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    # add string so it's read easier
    def __str__(self):
        return self.title