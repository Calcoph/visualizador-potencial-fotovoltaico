from django.contrib import admin
from .models import Parameter, Project, Data, Measure, Layer, Color, ColorRule, AllowedEmail

# Register your models here.
admin.site.register(Project)
admin.site.register(Color)
admin.site.register(ColorRule)
admin.site.register(Measure)
admin.site.register(Parameter)
admin.site.register(Layer)
admin.site.register(Data)
admin.site.register(AllowedEmail)
