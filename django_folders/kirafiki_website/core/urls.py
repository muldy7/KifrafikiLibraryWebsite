from django.urls import path
from . import views

#app_name = "core"

# these url names can be used for the "reverse" function to get urls
# I have to be very keen with all these names!
urlpatterns = [
    
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    path("home/", views.home_view, name="home"),
    
]
