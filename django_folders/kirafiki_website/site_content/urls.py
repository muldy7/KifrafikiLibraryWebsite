from django.urls import path
from . import views
 
app_name = "site_content"
 
urlpatterns = [
    path("", views.ContentListView.as_view(), name="content-list"),
    path("<slug:slug>/", views.ContentDetailView.as_view(), name="content-detail"),
    path("<slug:slug>/reader-view/", views.reader_view, name="reader-view"),
    path("<slug:slug>/update-content/", views.ContentUpdateView.as_view(),name="update-content"),
    path("<slug:slug>/delete-content/", views.ContentDeleteView.as_view(),name="delete-content"),
    path("fetch-database-entry/<str:word>/", views.fetch_database_entry, name="fetch-database-entry"),
]