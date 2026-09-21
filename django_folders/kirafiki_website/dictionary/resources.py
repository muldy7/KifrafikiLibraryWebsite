from import_export import resources
from .models import DictionaryEntry
from django.utils import timezone
from django.utils.text import slugify

class DictionaryEntryResource(resources.ModelResource):
    class Meta:
        model = DictionaryEntry
        # Exclude everything managed automatically to keep the schema clean
        exclude = ('slug', 'id', 'user_added', 'date_added', 'user_modified', 'date_modified')

    def get_import_id_fields(self):
        return []

    def before_save_instance(self, instance, row, **kwargs):
        """
        Runs right before the database insert/update command. 
        Assigning values here guarantees they bypass the spreadsheet clearing process.
        """
        user = kwargs.get('user')
        
        # 1. Handle dates safely
        instance.date_modified = timezone.now()
        if not instance.pk:  # If the instance has no Primary Key, it is brand new
            instance.date_added = timezone.now()

        # 2. Handle user assignments safely
        if user:
            instance.user_modified = user
            if not instance.pk:
                instance.user_added = user

        # make sure it gets a slug
        instance.slug = slugify(instance.swahili_entry)
                
        # Must return the super() or the row won't save at all!
        return super().before_save_instance(instance, row, **kwargs)
