from django import forms
from .models import BugReport
from dictionary.services import letter_counter
from django.core.exceptions import ValidationError

# form for bug report
class BugReportForm(forms.ModelForm):
    """
    Form for submitting a bug report and making sure there are good values
    """

    class Meta:
        model = BugReport
        fields = ["title","summary"]


    def clean(self):
        # get the cleaned data for each time the form is saved
        cleaned_data = super().clean()

        # grab values for testing
        title = cleaned_data.get('title') # the body of the article, maybe I change this name later but too late
        report = cleaned_data.get('summary')

        if report is None:
            # go back if nothing was submited
            return cleaned_data
        
        # only proceed if we have both values 
        if title:
            # there should be at least two characters in the word
            characters_required = 2

            # count letters in the swahili word
            letter_count_title = letter_counter(title)

            # count the letters in the english definition
            letter_count_body = letter_counter(report)

            # return an error in case any of them are empty strings
            if letter_count_body < characters_required:
                # we need to submit a bad form
                self.add_error('summary', ValidationError("Please submit a valid report"))

            # check the swahili entry too
            if letter_count_title < characters_required:
                self.add_error('title', ValidationError("Please submit a valid title"))

            # get the hell out of here if there's an error and we don't need to finish
            if self.errors:
                return cleaned_data

        # FIX 3: Always return the full cleaned_data dictionary from clean()
        return cleaned_data
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)