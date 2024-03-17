function anadir_atributo() {
    let nodo_nuevo_nombre = document.getElementById("name")
    let nuevo_nombre = nodo_nuevo_nombre.value
    nodo_nuevo_nombre.value = ""

    let nodo_nuevo_display_name = document.getElementById("display_name")
    let nuevo_display_name = nodo_nuevo_display_name.value
    nodo_nuevo_display_name.value = ""

    let xhttp = new XMLHttpRequest()

    xhttp.open("POST", "/map/api/newAttribute", true)
    xhttp.setRequestHeader("content-type", "application/x-www-form-urlencoded")
    let params = "name=" + encodeURIComponent(nuevo_nombre) + "&display_name=" + encodeURIComponent(nuevo_display_name)
    xhttp.send(params)

    let nuevo_li = document.createElement("li")
    nuevo_li.innerText = `${nuevo_display_name} (${nuevo_nombre})`
    document.getElementById("lista").appendChild(nuevo_li)
}
