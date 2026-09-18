from django.urls import path
from .views import UserVocabularyListView, VocabListDeleteView, ListAdditionDeleteView
from . import views

app_name = 'vocabulary'  # Optional: helps with namespacing your URLs

urlpatterns = [
    # Since it fetches data based on the logged-in user, the path can be clean
    path('', UserVocabularyListView.as_view(), name='my-vocab-list'),
    path('add-vocabulary-word/<str:word>/', views.add_vocabulary_word, name="add-vocabulary-word"),
    path("<int:pk>/delete-word/", views.ListAdditionDeleteView.as_view(),name="delete-word"),
    path("<int:pk>/delete-list/", views.VocabListDeleteView.as_view(),name="delete-list"),
]