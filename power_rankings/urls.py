from django.conf.urls import url
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("",views.create_power_rankings,name='create_power_rankings')
]
