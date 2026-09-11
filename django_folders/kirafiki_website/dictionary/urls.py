from django.urls import path
from . import views

app_name = "dictionary"

# these url names can be used for the "reverse" function to get urls
# I have to be very keen with all these names!
urlpatterns = [
    
    path("", views.DictionaryListView.as_view(), name="dictionary-list"),
    path("add-content/", views.add_content_view, name="add-content"),
    path("translate-suggestion/<str:word>/", views.translate_suggestion, name="translate-suggestion"),
    
    # want to have this one last since the slug can mess it up
    path("<slug:slug>/", views.DictionaryDetailView.as_view(), name="dictionary-detail"),
    path("<slug:slug>/update-entry/", views.DictionaryUpdateView.as_view(),name="update-entry"),
    path("<slug:slug>/delete-entry/", views.DictionaryDeleteView.as_view(),name="delete-entry"),
    
]
