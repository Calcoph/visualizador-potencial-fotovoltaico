function editParameter() {
    let form_data = new FormData(getForm())
    let name = form_data.get("name");
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editParameter", true);
    xhttp.send(form_data)

    let titleNameNode = document.getElementById("title_name");
    titleNameNode.innerHTML = name
}

function getForm() {
    document.getElementById("formEditParameter")
}

function deleteParameter() {
    let form_data = new FormData(getForm())
    let id = new FormData()
    id.set("id", form_data.get("id"))

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/deleteParameter", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirm_delete_parameter()
            } else {
                let error = get_error_string(this) // from error.js
                window.alert(error)
            }
        }
    }
    xhttp.send(id)

    document.getElementById('delete-confirm').close()
}

function confirm_delete_parameter() {
    let name = document.getElementById("title_name").textContent

    window.alert(interpolate(gettext("El parámetro %s se ha eliminado correctamente"), name))
    redirectProjectAdmin()
}

function redirectProjectAdmin() {
    window.location.href = "/map/project-admin"
}
