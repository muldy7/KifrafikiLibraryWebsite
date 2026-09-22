# code for creating the urls for the site
# going to use generic views, more complicated views need full on code

from django.urls import path
from . import views

# can add more views if I need them I guess
app_name = "accounts"

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name="signup")
]