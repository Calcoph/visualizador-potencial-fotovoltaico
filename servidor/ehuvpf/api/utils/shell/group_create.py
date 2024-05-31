# This script creates sensible default permission groups.
# The script (like all in this directory) must be manually
# executed using the django shell.
# Check this directory's README.md for more info.

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from api.utils.user import Permission
from django.contrib.auth.models import Permission as DjPermission

djpermission = lambda x: DjPermission.objects.get(codename=x)

no_content_type = ContentType(app_label='ehuvpf', model='no_model')
no_content_type.save()
# If no_content_type was already created:
# no_content_type = ContentType.objects.get(app_label='ehuvpf', model='no_model')


p = DjPermission.objects.create(
    codename=Permission.AdminEditProject,
    name="Permission for accessing admin pages such as \"project-admin\" and \"edit-project-details\"",
    content_type=no_content_type
)

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
    djpermission(Permission.ParameterEdit),
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
