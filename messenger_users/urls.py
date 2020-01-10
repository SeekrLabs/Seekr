from django.urls import path

from . import views

urlpatterns = [
    path('', views.messenger_user_create, name='index')
]