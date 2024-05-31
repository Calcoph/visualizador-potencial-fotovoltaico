function editar_atributo() {
    let form_data = new FormData(document.getElementById("formEditAttribute"))
    let nombre = form_data.get("display_name");
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editAttribute", true);
    xhttp.send(form_data)

    let nodo_nombre_titulo = document.getElementById("title_name");
    nodo_nombre_titulo.innerHTML = nombre
}
