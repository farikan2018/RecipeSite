from django.urls import path
from .views import *



urlpatterns = [
    path('', HomeTank.as_view(), name='home'),
]