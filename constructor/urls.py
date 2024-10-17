from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main_page, name='main'),
    path('start/', views.start, name='start'),
    path('start/check/name/', views.checkName),
    path('model/check/', views.checkModel),
    path('model/create/', views.createModel),

]
