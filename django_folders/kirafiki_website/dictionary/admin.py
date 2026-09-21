from django.contrib import admin
from .models import DictionaryEntry
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.utils import timezone
from .resources import DictionaryEntryResource
# Register your models here.
# have to register the model after they are made

# admin.site.register(DictionaryEntry)    # register dictionary entry

# register with the mixin
@admin.register(DictionaryEntry)
class DictionaryEntryAdmin(ImportExportModelAdmin):
    resource_classes = [DictionaryEntryResource]
    search_fields = ['swahili_entry','slug']
    ordering = ['swahili_entry'] 

    