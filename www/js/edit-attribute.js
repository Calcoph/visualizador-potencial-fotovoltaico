function getForm() {
    return document.getElementById("formEditAttribute")
}

function editAttribute() {
    let form_data = new FormData(getForm())
    let displayName = form_data.get("display_name");
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editAttribute", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirm_edit_attribute(displayName)
            } else {
                let error = get_error_string(this) // de error.js
                window.alert(error)
            }
        }
    }
    xhttp.send(form_data)
}

function confirm_edit_attribute(displayName) {
    let titleNameNode = document.getElementById("title_name");
    titleNameNode.innerHTML = displayName

    window.alert(gettext("Atributo editado correctamente"))
}

function deleteAttribute() {
    let form_data = new FormData(getForm())
    let id = new FormData()
    id.set("id", form_data.get("id"))

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/deleteAttribute", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirm_delete_attribute()
            } else {
                let error = get_error_string(this) // de error.js
                window.alert(error)
            }
        }
    }
    xhttp.send(id)

    document.getElementById('delete-confirm').close()
}

function confirm_delete_attribute() {
    let name = document.getElementById("title_name").textContent

    window.alert(interpolate(gettext("El atributo %s se ha eliminado correctamente"), name))
    redirectProjectAdmin()
}

function redirectProjectAdmin() {
    window.location.href = "/map/project-admin"
}
