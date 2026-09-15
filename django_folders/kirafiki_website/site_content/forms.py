from django import forms
from .models import Content
from dictionary.services import letter_counter
from django.core.exceptions import ValidationError
from django.utils.text import slugify


# this form is for the basic entry form for changing our story's content 
# form file for having a way to upload stories to the website
class ContentUpdateForm(forms.ModelForm):
    """
    One form = one row in the word table.
    ModelForm automatically builds form fields that match the model fields
    listed in Meta.fields, and knows how to save() directly to that model.
    """

    class Meta:
        model = Content
        fields = ["title", "content","level", "source"]

    def clean(self):
        # get the cleaned data for each time the form is saved
        cleaned_data = super().clean()

        # grab values for testing
        body = cleaned_data.get('content') # the body of the article, maybe I change this name later but too late
        title = cleaned_data.get('title')

        if body is None:

            # go back if nothing was submited
            return cleaned_data
        # only proceed if we have both values 
        if title:
            # there should be at least two characters in the word
            characters_required = 2

            # count letters in the swahili word
            letter_count_title = letter_counter(title)

            # count the letters in the english definition
            letter_count_body = letter_counter(body)

            # return an error in case any of them are empty strings
            if letter_count_body < characters_required:
                # we need to submit a bad form
                self.add_error('content', ValidationError("Please submit a valid text"))

            # check the swahili entry too
            if letter_count_title < characters_required:
                self.add_error('title', ValidationError("Please submit a valid title"))

            # get the hell out of here if there's an error and we don't need to finish
            if self.errors:
                return cleaned_data

            # Check if ANY OTHER entry already has the same slug
            # We'll keep punctuation as long as the slug is different
            slug = slugify(title)
            if Content.objects.filter(slug=slug).exclude(pk=self.instance.pk).exists():
                # Passing "swahili_entry" as the first argument attaches the error directly to the field in the UI
                self.add_error('title', ValidationError("This title already exists (case-insensitive and exlcuding punctuation)."))

        # FIX 3: Always return the full cleaned_data dictionary from clean()
        return cleaned_data
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Bring back your TextChoices to use as suggestions
        #dropdown_suggestions = [choice[0] for choice in Content.Levels.choices]

        
        # 3. Inject the options into the form instance metadata
        #self.fields['translation_source'].choices_list = dropdown_suggestions