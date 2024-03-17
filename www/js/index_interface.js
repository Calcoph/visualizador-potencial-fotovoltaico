let current_tab = undefined

function init() {
    init_map()
    set_current_tab()
    change_tab(current_tab)
    carga_atributos()
}

function set_current_tab() {
    let tab_html = document.getElementById("tab-select")
    for (const label of tab_html.children) {
        let input = label.children[0]
        if (input.checked) {
            console.log(input.value)
            current_tab = input.value
        }
    }
}

/**
 * @param {String} tab
 */
function change_tab(tab) {
    current_tab = tab
    let tab_html = document.getElementById("tab");
    tab_html.innerHTML = ""
    switch (tab) {
        case "atributos":
            tab_atributos(tab_html)
            break
        case "marcadores":
            tab_marcadores(tab_html)
            break
        case "mis edificios":
            tab_mis_edificios(tab_html)
            break
        case "capas":
            tab_capas(tab_html)
            break
        default:
            tab_html.innerHTML = ""
            break
    }
}


let available_attributes = []
function carga_atributos() {
    fetch("/map/api/getAttributes")
        .then(response => response.json())
        .then((json) => {
            available_attributes = json.available_attributes

            if (current_tab === "atributos") {
                change_tab(current_tab)
            }
        })
}

/**
 * @param {HTMLElement} tab
 */
function tab_atributos(tab) {
    available_attributes.forEach(function(atributo) {
        let label = document.createElement("label");
        let input = document.createElement("input")
        input.type = "checkbox"
        input.value = atributo.display_name
        input.name = atributo.name
        input.checked = SELECTED_ATTRIBUTES.find(function(selected_attribute) {
            return selected_attribute.name == atributo.name
        }) !== undefined
        input.onclick = update_selected_attributes
        label.appendChild(input)
        let att = document.createTextNode(atributo.display_name);
        label.appendChild(att)

        tab.appendChild(label)
    })
}

/**
 * @param {HTMLElement} tab
 */
function tab_marcadores(tab) {
    let inputs = ["marcador1", "marcador2", "marcador3", "marcador4", "marcador5"]
    inputs.forEach(function(nombre_marcador) {
        let button = document.createElement("button");
        let nombre = document.createTextNode(nombre_marcador);
        button.appendChild(nombre);

        tab.appendChild(button)
    })
}

/**
 * @param {HTMLElement} tab
 */
function tab_mis_edificios(tab) {
    let inputs = ["edificio1", "edificio2", "edificio3", "edificio4", "edificio5"]
    inputs.forEach(function(nombre_edificio) {
        let button = document.createElement("button");
        let nombre = document.createTextNode(nombre_edificio);
        button.appendChild(nombre);

        tab.appendChild(button)
    })
}

/**
 * @param {HTMLElement} tab
 */
function tab_capas(tab) {
    for (layer_key in LAYERS) {
        /** @type {AttributeLayer} */
        let layer = LAYERS[layer_key]

        let label = document.createElement("label");
        let input = document.createElement("input")
        input.setAttribute("type", "radio")
        input.setAttribute("name", "a")
        label.appendChild(input)
        let nombre = document.createTextNode(layer.display_name);
        label.appendChild(nombre)

        tab.appendChild(label)
    }
}
