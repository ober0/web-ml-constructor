from django.db import models

class Models(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False, unique=True)
