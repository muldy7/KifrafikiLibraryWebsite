from django.contrib import admin
from .models import Content, Lesson

# I can add some stuff here to make the stories searchable in admin
# Register your models here.
admin.site.register(Content)
admin.site.register(Lesson)
