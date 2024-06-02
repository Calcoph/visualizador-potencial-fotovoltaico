class Permission:
    # Permissions created manually
    AdminEditProject = "api.admin_edit_project"

    # Permissions created by django
    ProjectAdd = "api.add_project"
    ProjectEdit = "api.change_project"
    ProjectDelete = "api.delete_project"
    ProjectView = "api.view_project"

    PreprocessingInfoAdd = "api.add_preprocessinginfo"
    PreprocessingInfoEdit = "api.change_preprocessinginfo"
    PreprocessingInfoDelete = "api.delete_preprocessinginfo"
    PreprocessingInfoView = "api.view_preprocessinginfo"

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

    BuildingAdd = "api.add_building"
    BuildingEdit = "api.change_building"
    BuildingDelete = "api.delete_building"
    BuildingView = "api.view_building"
