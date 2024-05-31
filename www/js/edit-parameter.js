function editar_parametro() {
    let form_data = new FormData(document.getElementById("formEditParameter"))
    let nombre = form_data.get("name");
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editParameter", true);
    xhttp.send(form_data)

    let nodo_nombre_titulo = document.getElementById("title_name");
    nodo_nombre_titulo.innerHTML = nombre
}
