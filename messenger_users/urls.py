from django.urls import path

from . import views

urlpatterns = [
    path('create', views.create_messenger_user, name='create'),
    path('search', views.search_jobs, name='search'),
    path('verify_linkedin_url', views.confirm_linkedin_profile, name='verify_linkedin_url'),
    path('save_posting', views.save_posting, name='save_posting'),
    path('view_posting', views.view_posting, name='view_posting'),
    path('remove_saved_posting', views.remove_saved_posting, name='remove_saved_posting'),
    path('browse_saved_postings', views.browse_saved_postings, name='browse_saved_postings'),
    path('suggest_linkedin', views.suggest_linkedin, name='suggest_linkedin')
]