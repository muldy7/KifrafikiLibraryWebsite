from django import forms
from .models import DictionaryEntry
from django.core.exceptions import ValidationError
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
        swahili_entry = cleaned_data.get('swahili_entry').lower()

        if swahili_entry:
            # FIX 2: Convert to lowercase and save it back into the cleaned_data dict
            # not sure if I need to do this twice but doesn't hurt
            no_string_entry = swahili_entry.strip(string.punctuation)
            swahili_entry_lower = no_string_entry.lower()
            cleaned_data['swahili_entry'] = swahili_entry_lower

            # Check if ANY OTHER entry already has this lowercase swahili_entry
            if DictionaryEntry.objects.filter(swahili_entry=swahili_entry_lower).exclude(pk=self.instance.pk).exists():
                # Passing "swahili_entry" as the first argument attaches the error directly to the field in the UI
                self.add_error('swahili_entry', ValidationError("This entry already exists (should be all lowercase with no punctuation)."))

        # FIX 3: Always return the full cleaned_data dictionary from clean()
        return cleaned_data

        # going to make sure the slug will be okay since that seems easier
        # def clean_slug(self):
        #     slug = slugify(self.object.swahili_entry)
        #     slug = self.cleaned_data.get(slug)
            
        #     # Check if ANY OTHER entry already has this slug
        #     # We exclude the current instance (self.instance.pk) because updating 
        #     # your own slug to the same value is perfectly fine!
        #     queryset = DictionaryEntry.objects.filter(slug=slug)
        #     if self.instance.pk:
        #         queryset = queryset.exclude(pk=self.instance.pk)
                
        #     if queryset.exists():
        #         raise forms.ValidationError("An entry with this slug already exists.")
                
        #     return slug

# form file for having a way to upload stories to the website
class DictionaryEntryForm(forms.ModelForm):
    """
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Bring back your TextChoices to use as suggestions
        dropdown_suggestions = [choice[0] for choice in DictionaryEntry.TransSource.choices]
        
        # 2. Change the widget to a TextInput linked to an HTML <datalist>
        self.fields['translation_source'].widget = forms.TextInput(attrs={
            'list': 'translation_source_options',
            'placeholder': 'Select or type custom source...'
        })
        
        # 3. Inject the options into the form instance metadata
        self.fields['translation_source'].choices_list = dropdown_suggestions