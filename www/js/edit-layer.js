function addAttribute(id) {
    let attributeName = document.getElementById(`att_${id}`).getAttribute("name")

    domAddAttribute(id)
    addColorAttribute(id, attributeName)
}

function addColorAttribute(id, attributeName) {
    let selector = document.getElementById("attribute-color-selector")
    let newOption = document.createElement("option")
    newOption.textContent = attributeName
    newOption.value = id
    selector.appendChild(newOption)
}

function removeAttribute(id) {
    let attributeList = document.getElementById("attributes")
    if (attributeList.children.length <= 1) {
        window.alert(`
            Debe haber al menos 1 atributo por cada capa.
            Si quieres quitar este atributo, debes primero añadir otro.
        `)// TODO: Translate
        return;
    }
    let selected_id = document.getElementById("attribute-color-selector")
        .selectedOptions[0]
        .value

    if (selected_id == id) {
        window.alert(`
            No se puede eliminar el atributo a colorear.
            Si quieres quitar este atributo, debes primero
            cambiar el atributo a colorear.
        `)// TODO: Translate
        return;
    }

    domRemoveAttribute(id)
    removeColorAttribute(id)
}

function removeColorAttribute(id) {
    let selector = document.getElementById("attribute-color-selector")
    for (const option of selector) {
        if (option.value == id) {
            option.remove()
        }
    }
}

function domMoveAttribute(id, idDestList, newButtonText, newButtonFunction) {
    let oldAttribute = document.getElementById(`att_${id}`)
    oldAttribute.remove()
    let oldButton = undefined
    for (const child of oldAttribute.children) {
        if (child.tagName.toLowerCase() === "input") {
            oldButton = child
            break
        }
    }
    oldButton.onclick = newButtonFunction
    oldButton.value = newButtonText

    let destList = document.getElementById(idDestList)
    destList.appendChild(oldAttribute)
}

function domRemoveAttribute(id) {
    domMoveAttribute(
        id,
        "available-attributes",
        "Añadir", // TODO: Translate
        function() {addAttribute(id)}
    )
}

function domAddAttribute(id) {
    domMoveAttribute(
        id,
        "attributes",
        "Quitar", // TODO: Translate
        function() {removeAttribute(id)}
    )
}

function getForm() {
    return document.getElementById("edit-layer-form")
}

function validateForm() {
    let form = getForm()
    let attributes = document.getElementById("attributes")
    for (const atributo of attributes.children) {
        let hidden_attribute = document.createElement("input")
        hidden_attribute.type = "hidden"
        hidden_attribute.name = "attribute"
        hidden_attribute.value = atributo.value
        form.appendChild(hidden_attribute)
    }
    return true
}

function deleteLayer() {
    let form_data = new FormData(getForm())
    let id = new FormData()
    id.set("id", form_data.get("id"))

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/deleteLayer", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirm_delete_layer()
            } else {
                let error = get_error_string(this) // from error.js
                window.alert(error)
            }
        }
    }
    xhttp.send(id)

    document.getElementById('delete-confirm').close()
}

function confirm_delete_layer() {
    let name = document.getElementById("title_name").textContent

    window.alert(`La capa ${name} se ha eliminado correctamente`)// TODO: Translate
    redirectProjectAdmin()
}

function redirectProjectAdmin() {
    window.location.href = "/map/project-admin"
}
