class Permission:
    # Permissions created manually
    AdminEditProject = "admin_edit_project"

    # Permissions created by django
    ProjectAdd = "add_project"
    ProjectEdit = "change_project"
    ProjectDelete = "delete_project"
    ProjectView = "view_project"

    PreprocessingInfoAdd = "add_preprocessingInfo" # TODO: test these permissions
    PreprocessingInfoEdit = "change_preprocessingInfo"
    PreprocessingInfoDelete = "delete_preprocessingInfo"
    PreprocessingInfoView = "view_preprocessingInfo"

    ColorAdd = "add_color"
    ColorEdit = "change_color"
    ColorDelete = "delete_color"
    ColorView = "view_color"

    colorRuleAdd = "add_colorRule" # TODO: test these permissions
    colorRuleEdit = "change_colorRule"
    colorRuleDelete = "delete_colorRule"
    colorRuleView = "view_colorRule"

    MeasureAdd = "add_measure"
    MeasureEdit = "change_measure"
    MeasureDelete = "delete_measure"
    MeasureView = "view_measure"

    ParameterAdd = "add_parameter"
    ParameterEdit = "change_parameter"
    ParameterDelete = "delete_parameter"
    ParameterView = "view_parameter"

    LayerAdd = "add_layer"
    LayerEdit = "change_layer"
    LayerDelete = "delete_layer"
    LayerView = "view_layer"

    BuildingAdd = "add_building"
    BuildingEdit = "change_building"
    BuildingDelete = "delete_building"
    BuildingView = "view_building"
