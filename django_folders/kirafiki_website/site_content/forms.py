from django import forms
from .models import Content

# this form is for the basic entry form for changing our story's content 
# form file for having a way to upload stories to the website
class ContentEntryForm(forms.ModelForm):
    """
    One form = one row in the word table.
    ModelForm automatically builds form fields that match the model fields
    listed in Meta.fields, and knows how to save() directly to that model.
    """

    class Meta:
        model = Content
        fields = ["title", "content","level", "source"]

        # don't think we need this for the form 
        #widgets = {
            # The word itself comes from the story text, not from manual typing,
            # so we make it read-only in the browser. It's still submitted with
            # the form (readonly inputs still POST their value), just not editable.
            # this is not editable but maybe we will want to edit it in the future
         #   "swahili_entry": forms.TextInput(attrs={"readonly": "readonly"}),
        #}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 1. Bring back your TextChoices to use as suggestions
        #dropdown_suggestions = [choice[0] for choice in Content.Levels.choices]

        
        # 3. Inject the options into the form instance metadata
        #self.fields['translation_source'].choices_list = dropdown_suggestions