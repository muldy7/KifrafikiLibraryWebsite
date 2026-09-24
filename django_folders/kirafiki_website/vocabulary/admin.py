from django.contrib import admin
from .models import VocabularyList, ListAddition

# Register your models here.
admin.site.register(ListAddition)
#admin.site.register(VocabularyList)

# mae sure that the associations are shown on the admin page
class ListAdditionInline(admin.TabularInline):
    # Use the .through model attached to the many-to-many field
    model = VocabularyList.vocab_words.through 
    extra = 0  # Number of empty extra rows to display
    raw_id_fields = ['word'] 

@admin.register(VocabularyList)
class VocabularyListAdmin(admin.ModelAdmin):
    inlines = [ListAdditionInline, ]