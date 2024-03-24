"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from authentication.views import login, test_token, create_user
from media.views import media, telegram, update_database, edit_page_source, update_telegram

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login),
    path('create/', create_user),
    path('test_token/', test_token),
    path('media/', media),
    path('telegram/', telegram),
    path('update-database/', update_database),
    path('telegram-iframe/', edit_page_source),
    path('update-telegram/', update_telegram)
]
