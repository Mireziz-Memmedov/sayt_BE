from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name='signup'),
    path("verify/", views.verify, name='verify'),
    path("login/", views.login, name='login'),
    path("add_listing/", views.add_listing, name='add_listing'),
    path("listing_detail/", views.listing_detail, name='listing_detail'),
]