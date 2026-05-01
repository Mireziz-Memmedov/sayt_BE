from django.urls import path
from . import views

urlpatterns = [
    path("demo/", demo_api),
]