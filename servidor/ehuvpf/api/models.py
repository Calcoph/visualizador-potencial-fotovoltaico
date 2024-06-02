from django.db import models

from .utils.user import Permission

# Create your models here.
class Project(models.Model):
    """
    name: str
    data_source: str
    """
    name = models.TextField()
    data_source = models.TextField()

    class Meta:
        permissions = [
            (Permission.AdminEditProject, "Permission for accessing admin pages such as \"project-admin\" and \"edit-project-details\"")
        ]

class PreprocessingInfo(models.Model):
    """
    project: Project
    program_name: str
    program_link: str
    program_version: str
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    program_name = models.TextField()
    program_link = models.TextField()
    program_version = models.TextField()

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
    description: str
    unit: str
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.TextField()
    display_name = models.TextField()
    description = models.TextField()
    unit = models.TextField()

class Parameter(models.Model):
    """
    project: Project
    name: str
    description: str
    value: str
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.TextField()
    description = models.TextField()
    value = models.TextField() # It is a text in case there are non-numeric parameters

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
