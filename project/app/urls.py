from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("add/", views.add_telegram_user),
    path("show/", views.get_telegram_user),
]
