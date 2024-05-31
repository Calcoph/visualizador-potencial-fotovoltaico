function anadir_parametro() {
    let form_data = new FormData(document.getElementById("formAddParameter"))
    let nombre = form_data.get("name");
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/addParameter", true);
    xhttp.send(form_data)

    let nodo_nuevo_nombre = document.getElementById("name")
    nodo_nuevo_nombre.value = ""

    let nodo_descripcion = document.getElementById("description")
    nodo_descripcion.value = ""

    let nodo_valor = document.getElementById("value")
    nodo_valor.value = ""

    let nuevo_li = document.createElement("li")
    nuevo_li.innerText = `${nombre}`
    document.getElementById("lista").appendChild(nuevo_li)
}
