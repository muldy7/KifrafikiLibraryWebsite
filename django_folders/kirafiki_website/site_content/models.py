from django.db import models
from accounts.models import CustomUser
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

# IMPORTANT LINKS
# https://docs.djangoproject.com/en/6.1/topics/db/examples/one_to_one/
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
    source = models.CharField(max_length=500,default="No source found", help_text="Where is this content from? (URL, etc.)") # for setting where the article may be sourced from through a link

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


class Lesson(models.Model):
    """
    Each content on the website has an associated lesson that can be added to explain stuff that is going on in the
    content. 

    Link for the CKEDITOR project: https://pypi.org/project/django-ckeditor-5/
    (Lesson here is to always look for a human guide when implementing an app)
    """
    content = models.OneToOneField(Content, # add it as a one to one field so one content has one lesson
        on_delete=models.CASCADE,
        primary_key=True,
    ) 
    # add the lesson body
    body = CKEditor5Field('Lesson',blank=False, null=True, config_name="extends")

    # slug field for better urls
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    # change the stuff for modification
    # have to make some changes to the names so they don't clash
    last_edit = models.DateTimeField("Last Modified")
    user_edited = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="user_edited")
    
    # ue slugify to make a nice url out of the title
    def save(self, *args, **kwargs):
        if not self.slug:
            # add the slug to match it's content since we space the url with "lessons"
            self.slug = self.content.slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Lesson for: {self.content.title}" # add the name to be the less for: [whatever the associated content is]