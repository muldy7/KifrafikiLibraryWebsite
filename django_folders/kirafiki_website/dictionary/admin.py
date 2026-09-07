from django.contrib import admin
from .models import DictionaryEntry

# Register your models here.
# have to register the model after they are made

admin.site.register(DictionaryEntry)    # register dictionary entry
