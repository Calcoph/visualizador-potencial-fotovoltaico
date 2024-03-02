from django.db import models

# Create your models here.
class Project(models.Model):
    name = models.TextField()

class Building(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        primary_key=True
    )
    path = models.TextField()
    lat = models.IntegerField()
    lon = models.IntegerField()
