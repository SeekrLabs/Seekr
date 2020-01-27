from django.urls import path

from . import views

urlpatterns = [
    path('', views.search_jobs, name='index'),
    path('create', views.create_messenger_user, name='create'),
    path('search', views.search_jobs, name='search'),
    path('verifyLinkedIn', views.confirm_linkedin_profile, name='verifyLinkedIn')
]