"""
URL configuration for kirafiki_website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include 

# have to add the urls from each app to the global urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), 
    path('accounts/', include('django.contrib.auth.urls')), # add basic login page
    path('site_content/', include('site_content.urls')),
    path('dictionary/', include('dictionary.urls')),
    path('', include('core.urls')),
    path('my-vocabulary/',include('vocabulary.urls')), # want to change this later
]


