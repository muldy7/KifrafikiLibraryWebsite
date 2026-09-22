from django.contrib import admin
from .models import CustomUser
from django.contrib.auth import get_user_model
# Register your models here.

# # RUN ON FIRST DEPLOY OF THE WEBSITE
# if not CustomUser.objects.filter(is_superuser=True).first():
#     user = CustomUser.objects.create(
#         username = 'admin',
#         email = 'example@gmail.com',
#         is_superuser = True,
#         user.is_staff = True,

#     )
#     user.set_password('some password') # <----- don't forget to change
#     user.save()

user = get_user_model()
# Replace 'username_here' with the actual username
user = CustomUser.objects.get(username="admin")

# Grant admin login access
user.is_staff = True

# Optional: Grant total control (bypasses all permission checks)
# user.is_superuser = True

user.save()
# register parts of the admin
admin.site.register(CustomUser)