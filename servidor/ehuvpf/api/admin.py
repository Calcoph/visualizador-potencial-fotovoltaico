from django.contrib import admin
from .models import Project, Building, Measure, Layer

# Register your models here.
admin.site.register(Project)
admin.site.register(Building)
admin.site.register(Measure)
admin.site.register(Layer)
