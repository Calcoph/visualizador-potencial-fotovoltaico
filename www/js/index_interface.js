let current_tab = undefined

function init() {
    init_map()
    set_current_tab()
    refrescar_tab()
    carga_atributos()
}

function set_current_tab() {
    let tab_html = document.getElementById("tab-select")
    for (const label of tab_html.children) {
        let input = label.children[0]
        if (input.checked) {
            current_tab = input.value
        }
    }
}

function refrescar_tab() {
    if (current_tab !== undefined) {
        change_tab(current_tab)
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
        case "attributes":
            tab_atributos(tab_html)
            break
        case "marcadores":
            tab_marcadores(tab_html)
            break
        case "mis edificios":
            tab_mis_edificios(tab_html)
            break
        case "layers":
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

            if (current_tab === "attributes") {
                change_tab(current_tab)
            }
        })
}

/**
 * @param {HTMLElement} tab
 */
function tab_atributos(tab) {
    let template = document.getElementById("attributes-tab").content.children[0];

    available_attributes.forEach(function(atributo) {
        /** @type {HTMLLabelElement} */
        let new_node = document.importNode(template, true);
        /** @type {HTMLInputElement} */
        let input = new_node.children[0]
        /** @type {HTMLSpanElement} */
        let span = new_node.children[1];

        // Fill input
        input.value = atributo.display_name
        input.name = atributo.name
        input.checked = SELECTED_ATTRIBUTES.find(function(selected_attribute) {
            return selected_attribute.name == atributo.name
        }) !== undefined

        // Fill span
        span.textContent = atributo.display_name

        tab.appendChild(new_node)

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
    let template = document.getElementById("layer-tab").content.children[0];

    for (layer_key in LAYERS) {
        /*
        This copy is needed, because layer_key
        changes but the value passed to
        onclick must be constant
        */
        let layer_name = layer_key // DO NOT DELETE THIS LINE (see comment above)

        let layer = LAYERS[layer_key]

        /** @type {HTMLLabelElement} */
        let new_node = document.importNode(template, true);
        /** @type {HTMLInputElement} */
        let input = new_node.children[0];
        /** @type {HTMLSpanElement} */
        let span = new_node.children[1];

        // Fill input
        if (layer_key === SELECTED_LAYER) {
            input.checked = true
        }
        input.onclick = function() {
            cambiar_capa(layer_name)
        }

        // Fill span
        span.textContent = layer.display_name;

        tab.appendChild(new_node)
    }
}
