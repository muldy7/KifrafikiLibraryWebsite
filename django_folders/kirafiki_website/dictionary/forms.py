from django import forms
from .models import DictionaryEntry
from django.core.exceptions import ValidationError
from .services import letter_counter
from django.utils.text import slugify
import string 

class DictionaryUpdateForm(forms.ModelForm):
    """
    This form is for using the update view to modify existing dictionary entries
    """
    class Meta:
        model = DictionaryEntry
        fields = ["swahili_entry", "english","part_of_speech", "swahili_definition","sentence", "construction", "translation_source"]

    # should not be indented in the meta class
    def clean(self):
        cleaned_data = super().clean()
        # make sure that the swahili entry is all lower case
        swahili_entry = cleaned_data.get('swahili_entry') # I don't want to lower case here because it might be empty
        english = cleaned_data.get('english')

        if english is None:
            # if there is a NoneType in the form, django automatically sends a message of "This field is required"
            # go back if there are a bunch of spaces in the entry 
            return cleaned_data
            
        # only proceed if we have both values 
        if swahili_entry:
            # there should be at least two characters in the word
            characters_required = 2

            # count letters in the swahili word
            letter_count_swahili = letter_counter(swahili_entry)

            # count the letters in the english definition
            letter_count_english = letter_counter(english)

            # return an error in case any of them are empty strings
            if letter_count_english < characters_required:
                # we need to submit a bad form
                self.add_error('english', ValidationError("Please submit a valid definition"))

            # check the swahili entry too
            if letter_count_swahili < characters_required:
                self.add_error('swahili_entry', ValidationError("Please submit a valid swahili word"))

            # get the hell out of here if there's an error and we don't need to finish
            if self.errors:
                return cleaned_data

            # clean the swahili entry if it's valid
            no_string_entry = swahili_entry.strip(string.punctuation)
            swahili_entry_lower = no_string_entry.lower()
            cleaned_data['swahili_entry'] = swahili_entry_lower

            # Check if ANY OTHER entry already has this lowercase swahili_entry
            if DictionaryEntry.objects.filter(swahili_entry=swahili_entry_lower).exclude(pk=self.instance.pk).exists():
                # Passing "swahili_entry" as the first argument attaches the error directly to the field in the UI
                self.add_error('swahili_entry', ValidationError("This entry already exists (should be all lowercase with no punctuation)."))

        # FIX 3: Always return the full cleaned_data dictionary from clean()
        return cleaned_data

        
# form file for having a way to upload stories to the website
class DictionaryEntryForm(forms.ModelForm):
    """
    This is used with the content tool for adding words from stories
    One form = one row in the word table.
    ModelForm automatically builds form fields that match the model fields
    listed in Meta.fields, and knows how to save() directly to that model.
    """

    class Meta:
        model = DictionaryEntry
        fields = ["swahili_entry", "english","part_of_speech", "swahili_definition","sentence", "construction", "translation_source"]
        widgets = {
            # The word itself comes from the story text, not from manual typing,
            # so we make it read-only in the browser. It's still submitted with
            # the form (readonly inputs still POST their value), just not editable.
            # this is not editable but maybe we will want to edit it in the future
            "swahili_entry": forms.TextInput(attrs={"readonly": "readonly"}),
        }

    # testing for the form submissions
    def clean(self):
        cleaned_data = super().clean()

        # just need to test english here and the other fields 
        english = cleaned_data.get('english')
        source = cleaned_data.get('translation_source')
        swahili_definition = cleaned_data.get('swahili_definition')
        sentence = cleaned_data.get('sentence')
        construction = cleaned_data.get('construction')
        part_of_speech = cleaned_data.get('part_of_speech')

        # make a list of the values
        values = [english,source, swahili_definition,sentence,construction,part_of_speech]
        # only proceed if we have all values 
        if all(item is not None for item in values):
            # there should be at least two characters in the word
            characters_required = 2

            letter_count_english = letter_counter(english)
            lc_source = letter_counter(source)
            lc_swahili_definition = letter_counter(swahili_definition)
            lc_sentence = letter_counter(sentence)
            lc_construction = letter_counter(construction)
            lc_part_of_speech = letter_counter(part_of_speech)

            # return an error in case any of them are empty strings
            if letter_count_english < characters_required:
                # we need to submit a bad form
                self.add_error('english', ValidationError("Please submit a valid definition"))

            # check the other fields
            if lc_source < characters_required:
                self.add_error('source', ValidationError("Please submit a valid entry for 'source'"))

            if lc_swahili_definition < characters_required:
                self.add_error('swahili_definition', ValidationError("Please submit a valid entry for 'swahili definition'"))

            if lc_sentence < characters_required:
                self.add_error('sentence', ValidationError("Please submit a valid entry for 'examples'"))

            if lc_construction < characters_required:
                self.add_error('construction', ValidationError("Please submit a valid entry for 'construction'"))

            if lc_part_of_speech < characters_required:
                self.add_error('part_of_speech', ValidationError("Please submit a valid entry for 'part_of_speech'"))

            # get the hell out of here if there's an error and we don't need to finish
            if self.errors:
                return cleaned_data

        elif english is None:
            # don't display an error if english is empty because there is already the "this field is required error"
            pass
        else: 
            # other fields need an error
            values = [source, swahili_definition,sentence,construction,part_of_speech]
            # add error for the empty fields
            for value in values:
                if value is None:
                    self.add_error(value, ValidationError("Please enter a value (or N/A)"))

        # Always return the full cleaned_data dictionary from clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        # what is done when the form saves
        # the only real thing that causes problems is when changing the name of the swahili_entry
        # for now don't need to add cleaning of the other forms I feel like

        super().__init__(*args, **kwargs)
      