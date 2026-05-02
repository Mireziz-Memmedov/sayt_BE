from django.urls import path
from . import views

urlpatterns = [
    path("demo/", views.demo_api, name='demo_api'),
]