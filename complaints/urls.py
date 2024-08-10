from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('',views.retrieve_complaints),
    path('register/',views.new_complaint,name="newComplaint"),
]