from django.contrib import admin
from .models import Parameter, PreprocessingInfo, Project, Building, Measure, Layer, Color, ColorRule

# Register your models here.
admin.site.register(Project)
admin.site.register(PreprocessingInfo)
admin.site.register(Color)
admin.site.register(ColorRule)
admin.site.register(Measure)
admin.site.register(Parameter)
admin.site.register(Layer)
admin.site.register(Building)
