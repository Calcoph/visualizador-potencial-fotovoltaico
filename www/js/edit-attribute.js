function editar_atributo() {
    let form_data = new FormData(document.getElementById("formEditAttribute"))
    let nombre = form_data.get("display_name");
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editAttribute", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirm_edit_attribute(nombre)
            } else {
                let error = get_error_string(this) // from error.js
                window.alert(error)
            }
        }
    }
    xhttp.send(form_data)
}

function confirm_edit_attribute(nombre) {
    let nodo_nombre_titulo = document.getElementById("title_name");
    nodo_nombre_titulo.innerHTML = nombre
}
