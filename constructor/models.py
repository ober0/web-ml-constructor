from django.db import models

class UserModels(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False, unique=True)
    DatasetPath = models.CharField(max_length=200, null=False, blank=False, unique=True)

class DataFields(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    datetype = models.CharField(max_length=20, null=False, blank=False)
    predictValue = models.CharField(max_length=100, null=False, blank=False)
    modelId = models.CharField(max_length=30, null=False, blank=False)
