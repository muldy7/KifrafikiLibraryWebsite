from django.urls import path
from .views import UserVocabularyListView
from . import views

app_name = 'vocabulary'  # Optional: helps with namespacing your URLs

urlpatterns = [
    # Since it fetches data based on the logged-in user, the path can be clean
    path('', UserVocabularyListView.as_view(), name='my-vocab-list'),
    path('add-vocabulary-word/<str:word>/', views.add_vocabulary_word, name="add-vocabulary-word")
]