function anadir_parametro() {
    let form_data = new FormData(get_form())
    let nombre = form_data.get("name");
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/addParameter", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirm_add_parameter(nombre)
            } else {
                let error = get_error_string(this)
                window.alert(error)
            }
        }
    }
    xhttp.send(form_data)
}

function confirm_add_parameter(name) {
    addItemToList(name)
    get_form().reset()
}

function get_form() {
    return document.getElementById("formAddParameter")
}
