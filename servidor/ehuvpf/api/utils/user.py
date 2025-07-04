class Permission:
    # Permissions created manually
    AdminEditProject = "api.admin_edit_project"
    DataSourceEdit = "api.data_source_edit"
    PreprocessingInfoEdit = "api.change_preprocessinginfo"

    # Permissions created by django
    ProjectAdd = "api.add_project"
    ProjectEdit = "api.change_project"
    ProjectDelete = "api.delete_project"
    ProjectView = "api.view_project"

    ColorAdd = "api.add_color"
    ColorEdit = "api.change_color"
    ColorDelete = "api.delete_color"
    ColorView = "api.view_color"

    colorRuleAdd = "api.add_colorrule"
    colorRuleEdit = "api.change_colorrule"
    colorRuleDelete = "api.delete_colorrule"
    colorRuleView = "api.view_colorrule"

    MeasureAdd = "api.add_measure"
    MeasureEdit = "api.change_measure"
    MeasureDelete = "api.delete_measure"
    MeasureView = "api.view_measure"

    ParameterAdd = "api.add_parameter"
    ParameterEdit = "api.change_parameter"
    ParameterDelete = "api.delete_parameter"
    ParameterView = "api.view_parameter"

    LayerAdd = "api.add_layer"
    LayerEdit = "api.change_layer"
    LayerDelete = "api.delete_layer"
    LayerView = "api.view_layer"

    DataAdd = "api.add_data"
    DataEdit = "api.change_data"
    DataDelete = "api.delete_data"
    DataView = "api.view_data"

    def permission_name(permission: str):
         # Split to remove the "api." at the start of the permission
        return permission.split(".", maxsplit=1)[1]
