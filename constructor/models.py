from django.db import models

class UserModels(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False, unique=True)
    DatasetPath = models.CharField(max_length=200, null=False, blank=False, unique=True)
    GraphisPath = models.CharField(max_length=200, null=True, blank=True, unique=True)
    LEPath = models.CharField(max_length=200, null=True, blank=True, unique=True)
    ModelPath = models.CharField(max_length=200, null=True, blank=True, unique=True)
    mse = models.FloatField(max_length=30, null=True, blank=False)
    api = models.TextField(null=True, blank=True)

class DataFields(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    datetype = models.CharField(max_length=20, null=False, blank=False)
    predictValue = models.CharField(max_length=100, null=False, blank=False)
    modelId = models.CharField(max_length=30, null=False, blank=False)
