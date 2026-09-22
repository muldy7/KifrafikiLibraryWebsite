from django.contrib import admin
from .models import CustomUser
# Register your models here.

# RUN ON FIRST DEPLOY OF THE WEBSITE
if not CustomUser.objects.filter(is_superuser=True).first():
    user = CustomUser.objects.create(
        username = 'admin',
        email = 'abe@muldrow.net',
        is_superuser = True,

    )
    user.set_password('#Django123@')
    user.save()

# register parts of the admin
admin.site.register(CustomUser)