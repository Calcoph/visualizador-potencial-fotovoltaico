from django.db import models

# Create your models here.
class Project(models.Model):
    name = models.TextField()

class Building(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    path = models.TextField()
    lat = models.IntegerField()
    lon = models.IntegerField()

class Measure(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.TextField()
