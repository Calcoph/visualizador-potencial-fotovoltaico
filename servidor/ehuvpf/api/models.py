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
    preprocess_program_name = models.TextField()
    preprocess_program_link = models.TextField()
    preprocess_program_version = models.TextField()

    class Meta:
        permissions = [
            (Permission.permission_name(Permission.AdminEditProject), "Permission for accessing admin pages such as \"project-admin\" and \"edit-project-details\""),
            (Permission.permission_name(Permission.DataSourceEdit), "Permission for editing the data source of the project"),
            (Permission.permission_name(Permission.PreprocessingInfoEdit), "Permission for editing the preprocessing info of the project"),
        ]

    def __str__(self):
        return f"{self.name}"

class Color(models.Model):
    """
    project: Project
    hex: str
    strength: int
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    hex = models.TextField()
    strength = models.IntegerField()

    def __str__(self):
        return f"{self.hex} ({self.strength})"

class ColorRule(models.Model):
    """
    color: Color
    minimum: float
    """
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    minimum = models.FloatField()

    def __str__(self):
        return f"{self.color.hex} > {str(self.minimum)}"

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

    def __str__(self):
        return f"{self.display_name}"

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

    def __str__(self):
        return f"{self.name}"

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
    color_measure = models.ForeignKey(Measure, on_delete=models.PROTECT, related_name="color_measure")
    color_rules = models.ManyToManyField(ColorRule)
    name = models.TextField()
    name_pattern = models.TextField()

    def __str__(self):
        return f"{self.name}"

class Data(models.Model):
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

    def __str__(self):
        return f"{self.lat},{self.lon} ({self.layer})"

class AllowedEmail(models.Model):
    """
    email: str
    """
    email = models.TextField()

    def __str__(self):
        return f"{self.email}"
