from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from postings import views

router = routers.DefaultRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('messenger_users/', include('messenger_users.urls')),
]
