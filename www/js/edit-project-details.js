function edit_preprocess_info() {
    let form_data = new FormData(document.getElementById("formEditPreprocessInfo"))
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editPreprocessInfo", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                window.alert("Se ha modificado la información de preprocesado adecuadamente.")
            } else {
                let error = get_error_string(this)
                window.alert(error)
            }
        }
    }
    xhttp.send(form_data)
}

function edit_data_source() {
    let form_data = new FormData(document.getElementById("formEditDataSource"))
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editDataSource", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                window.alert("Se ha modificado la información sobre la fuente de datos adecuadamente.")
            } else {
                let error = get_error_string(this)
                window.alert(error)
            }
        }
    }
    xhttp.send(form_data)
}
