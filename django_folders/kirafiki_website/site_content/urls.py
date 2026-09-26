from django.urls import path
from . import views
 
app_name = "site_content" # should probably change this to without a dash later
 
urlpatterns = [
    path("", views.ContentListView.as_view(), name="content-list"),
    path("<slug:slug>/", views.ContentDetailView.as_view(), name="content-detail"),
    path("<slug:slug>/reader-view/", views.reader_view, name="reader-view"),
    path("<slug:slug>/update-content/", views.ContentUpdateView.as_view(),name="update-content"),
    path("<slug:slug>/delete-content/", views.ContentDeleteView.as_view(),name="delete-content"),
    path("fetch-database-entry/<str:word>/", views.fetch_database_entry, name="fetch-database-entry"),
    path("<slug:slug>/update-lesson/", views.LessonUpdateView.as_view(),name="update-lesson"),
    path("lessons/<slug:slug>/", views.LessonDetailView.as_view(), name="lesson-detail"),
    path("<slug:slug>/add-a-lesson/", views.AddALesson.as_view(), name="add-a-lesson")
]