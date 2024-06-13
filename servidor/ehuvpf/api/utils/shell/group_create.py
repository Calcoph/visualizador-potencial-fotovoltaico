# This script creates sensible default permission groups.
# The script (like all in this directory) must be manually
# executed using the django shell.
# Check this directory's README.md for more info.

from django.contrib.auth.models import Group, User

from api.utils.user import Permission
from django.contrib.auth.models import Permission as DjPermission

djpermission = lambda x: DjPermission.objects.get(codename=Permission.permission_name(x))

data_contributor_permissions = [
    djpermission(Permission.BuildingAdd),
    djpermission(Permission.AdminEditProject)
]
data_contributor = Group(name="data_contributor")
data_contributor.save()
data_contributor.permissions.set(data_contributor_permissions)
data_contributor.save()

data_editor_permissions = [
    djpermission(Permission.MeasureAdd),
    djpermission(Permission.MeasureEdit),
    djpermission(Permission.LayerEdit),
    djpermission(Permission.LayerAdd),
    djpermission(Permission.ColorEdit),
    *data_contributor_permissions
]
data_editor = Group(name="data_editor")
data_editor.save()
data_editor.permissions.set(data_editor_permissions)
data_editor.save()

project_admin_permissions = [
    djpermission(Permission.ParameterAdd),
    djpermission(Permission.PreprocessingInfoEdit),
    djpermission(Permission.DataSourceEdit),
    djpermission(Permission.MeasureDelete),
    *data_contributor_permissions
]
project_admin = Group(name="project_admin")
project_admin.save()
project_admin.permissions.set(project_admin_permissions)
project_admin.save()

page_admin_permissions = [
    djpermission(Permission.ProjectAdd),
    *project_admin_permissions
]
page_admin = Group(name="page_admin")
page_admin.save()
page_admin.permissions.set(page_admin_permissions)
page_admin.save()
