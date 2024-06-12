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
        `)
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
        `)
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
        "Añadir",
        function() {addAttribute(id)}
    )
}

function domAddAttribute(id) {
    domMoveAttribute(
        id,
        "attributes",
        "Quitar",
        function() {removeAttribute(id)}
    )
}

function validateForm() {
    let form = document.getElementById("edit-layer-form")
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
