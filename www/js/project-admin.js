function anadir_atributo() {
    let nodo_nuevo_nombre = document.getElementById("nuevo-nombre")
    let nuevo_nombre = nodo_nuevo_nombre.value
    console.log(nuevo_nombre)
    nodo_nuevo_nombre.value = ""

    let xhttp = new XMLHttpRequest()

    xhttp.open("POST", "/map/api/newAttribute", true)
    xhttp.setRequestHeader("content-type", "application/x-www-form-urlencoded")
    let params = "name=" + encodeURIComponent(nuevo_nombre)
    xhttp.send(params)

    let nuevo_li = document.createElement("li")
    nuevo_li.innerText = nuevo_nombre
    document.getElementById("lista").appendChild(nuevo_li)
}
