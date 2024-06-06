function edit_preprocess_info() {
    let form_data = new FormData(document.getElementById("formEditPreprocessInfo"))
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editPreprocessInfo", true);
    xhttp.send(form_data)
}

function edit_data_source() {
    let form_data = new FormData(document.getElementById("formEditDataSource"))
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editDataSource", true);
    xhttp.send(form_data)
}
