from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('api/predict/model/<int:pk>/', views.predict_api),
    path('model/<int:pk>/request', views.request_predict),
]
