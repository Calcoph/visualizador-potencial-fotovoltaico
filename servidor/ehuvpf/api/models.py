from django.db import models

# Create your models here.
class Project(models.Model):
    name = models.TextField()

class Color(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    hex = models.TextField()
    strength = models.IntegerField()

class ColorRule(models.Model):
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    minimum = models.FloatField()

class Measure(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.TextField()
    display_name = models.TextField()

class Layer(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    default_measures = models.ManyToManyField(Measure)
    color_measure = models.ForeignKey(Measure, on_delete=models.CASCADE, related_name="color_measure")
    color_rules = models.ManyToManyField(ColorRule)
    name = models.TextField()
    name_pattern = models.TextField()

class Building(models.Model):
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE)
    path = models.TextField()
    lat = models.IntegerField()
    lon = models.IntegerField()
