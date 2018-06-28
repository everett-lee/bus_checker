from django.urls import path

from . import views

urlpatterns = [
    path('', views.tfl_search, name='home'),
]
