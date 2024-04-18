from django.db import models

# Create your models here.
class Project(models.Model):
    """
    name: str
    """
    name = models.TextField()

class Color(models.Model):
    """
    project: Project
    hex: str
    strength: int
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    hex = models.TextField()
    strength = models.IntegerField()

class ColorRule(models.Model):
    """
    color: Color
    minimum: float
    """
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    minimum = models.FloatField()

class Measure(models.Model):
    """
    project: Project
    name: str
    display_name: str
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.TextField()
    display_name = models.TextField()

class Layer(models.Model):
    """
    project: Project,
    default_measures: Set[Measure]
    color_measure: Measure
    color_rules: Set[ColorRule]
    name: str
    name_pattern: str
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    default_measures = models.ManyToManyField(Measure)
    color_measure = models.ForeignKey(Measure, on_delete=models.CASCADE, related_name="color_measure")
    color_rules = models.ManyToManyField(ColorRule)
    name = models.TextField()
    name_pattern = models.TextField()

class Building(models.Model):
    """
    layer: Layer
    path: str
    lat: int
    lon: int
    """
    layer = models.ForeignKey(Layer, on_delete=models.CASCADE)
    path = models.TextField()
    lat = models.IntegerField()
    lon = models.IntegerField()
