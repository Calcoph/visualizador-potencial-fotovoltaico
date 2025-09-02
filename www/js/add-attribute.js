function addAttribute() {
    let form_data = new FormData(get_form())
    let name = form_data.get("name");
    let display_name = form_data.get("display_name");

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/addAttribute", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirm_add_attribute(display_name, name)
            } else {
                let error = get_error_string(this)
                window.alert(error)
            }
        }
    }
    xhttp.send(form_data)
}

function confirm_add_attribute(display_name, name) {
    addItemToList(display_name, name)

    get_form().reset()
    window.alert(gettext("Atributo añadido correctamente"))
}

function get_form() {
    return document.getElementById("formAddAttribute")
}
