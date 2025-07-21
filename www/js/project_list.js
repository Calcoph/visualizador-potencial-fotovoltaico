function selectProjectRequest(id) {
    let xhttp = new XMLHttpRequest()

    xhttp.open("POST", "/map/api/selectProject", false) // synchronous request. Don't redirect until it has been completed
    xhttp.setRequestHeader("content-type", "application/x-www-form-urlencoded")
    let params = "project_id=" + id
    xhttp.send(params)
    if (xhttp.status != 200) {
        window.alert(get_error_string(xhttp))
        return
    }
}

function select_project(id) {
    let redirect = document.getElementById("next").value

    selectProjectRequest(id)

    if (redirect) {
        window.location.href = redirect
    } else {
        window.location.href = "/"
    }
}

function preprocessCheckbox() {
    let preprocessed = document.getElementById("preprocess-checkbox").checked
    let preprocess_input = document.getElementById("preprocess-input")
    preprocess_input.hidden = !preprocessed
}

function createProject() {
    let form_data = new FormData(document.getElementById("create-project-form"))

    let preprocessed = document.getElementById("preprocess-checkbox").checked
    if (!preprocessed) {
        form_data.delete("preprocess_name")
        form_data.delete("preprocess_link")
        form_data.delete("preprocess_version")
    }

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "api/createProject", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirmCreateProject(this.response)
            } else {
                let error = get_error_string(this) // from error.js
                window.alert(error)
            }
        }
    }
    xhttp.send(form_data)
}

function confirmCreateProject(id) {
    selectProjectRequest(id)

    window.location.href = "/map/project-admin"
}
