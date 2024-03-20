function anadir_atributo(id) {
    xhttp = new XMLHttpRequest()

    let nombre_atributo = document.getElementById(`att_${id}`).getAttribute("name")

    xhttp.open("POST", "/map/api/addAttribute", true)
    xhttp.setRequestHeader("content-type", "application/x-www-form-urlencoded")
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            dom_anadir_atributo(id)
            anadir_atributo_coloreable(id, nombre_atributo)
        } else if (this.readyState == 4) {
            alert(`No se ha podido añadir el atributo, error ${this.status}: ${this.statusText}`)
        }
    }
    let layer = document.getElementById("layer-id").value
    let params = "layer=" + encodeURIComponent(layer) + "&attribute=" + encodeURIComponent(id)
    xhttp.send(params)
}

function anadir_atributo_coloreable(id, nombre_atributo) {
    let selector = document.getElementById("seleccion-atributo-color")
    let opcion_nueva = document.createElement("option")
    opcion_nueva.textContent = nombre_atributo
    opcion_nueva.value = id
    selector.appendChild(opcion_nueva)
}

function quitar_atributo(id) {
    let lista_atributos = document.getElementById("atributos")
    if (lista_atributos.children.length <= 1) {
        window.alert(`
            Debe haber al menos 1 atributo por cada capa.
            Si quieres quitar este atributo, debes primero añadir otro.
        `)
        return;
    }
    let selected_id = document.getElementById("seleccion-atributo-color")
        .selectedOptions[0]
        .value

    if (selected_id == id) {
        window.alert(`
            No se puede eliminar el atributo a colorear.
            Si quieres quitar este atributo, debes primero
            cambiar el atributo a colorear.
        `)
        return;
    }

    let xhttp = new XMLHttpRequest()

    xhttp.open("POST", "/map/api/hideAttribute", true)
    xhttp.setRequestHeader("content-type", "application/x-www-form-urlencoded")
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            dom_quitar_atributo(id)
            quitar_atributo_coloreable(id)
        } else if (this.readyState == 4) {
            alert(`No se ha podido quitar el atributo, error ${this.status}: ${this.statusText}`)
        }
    }
    let layer = document.getElementById("layer-id").value
    let params = "layer=" + encodeURIComponent(layer) + "&attribute=" + encodeURIComponent(id)
    xhttp.send(params)
}

function quitar_atributo_coloreable(id) {
    let selector = document.getElementById("seleccion-atributo-color")
    for (const opcion of selector) {
        if (opcion.value == id) {
            opcion.remove()
        }
    }
}

function dom_mover_atributo(id, id_lista_objetivo, texto_boton_nuevo, funcion_nueva_boton) {
    let atributo_viejo = document.getElementById(`att_${id}`)
    atributo_viejo.remove()
    let boton_viejo = undefined
    for (const child of atributo_viejo.children) {
        if (child.tagName.toLowerCase() === "button") {
            boton_viejo = child
            break
        }
    }
    boton_viejo.onclick = funcion_nueva_boton
    boton_viejo.textContent = texto_boton_nuevo

    let lista_objetivo = document.getElementById(id_lista_objetivo)
    lista_objetivo.appendChild(atributo_viejo)
}

function dom_quitar_atributo(id) {
    dom_mover_atributo(
        id,
        "atributos-disponibles",
        "Añadir",
        function() {anadir_atributo(id)}
    )
}

function dom_anadir_atributo(id) {
    dom_mover_atributo(
        id,
        "atributos",
        "Quitar",
        function() {quitar_atributo(id)}
    )
}

function cambiar_atributo_color() {
    let xhttp = new XMLHttpRequest()

    xhttp.open("POST", "/map/api/changeColorAttribute", true)
    xhttp.setRequestHeader("content-type", "application/x-www-form-urlencoded")
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status != 200) {
            alert(`No se ha podido cambiar el atributo a colorear, error ${this.status}: ${this.statusText}`)
        }
    }
    let layer = document.getElementById("layer-id").value
    let selected_id = document.getElementById("seleccion-atributo-color")
        .selectedOptions[0]
        .value
    let params = "layer=" + encodeURIComponent(layer) + "&color_attribute=" + encodeURIComponent(selected_id)
    xhttp.send(params)
}
