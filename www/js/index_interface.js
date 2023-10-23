
function init() {
    init_map()
}

/**
 * @param {String} tab
 */
function change_tab(tab) {
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
        default:
            tab_html.innerHTML = ""
            break
    }
}

/**
 * @param {HTMLElement} tab
 * 
 * @returns {String}
 */
function tab_atributos(tab) {
    let inputs = ["count", "sum", "mean", "median", "stdev", "min", "max", "range", "minority", "majority", "variety", "variance"]
    inputs.forEach(function(atributo) {
        let label = document.createElement("label");
        let input = document.createElement("input")
        input.setAttribute("type", "radio")
        input.setAttribute("name", "a")
        label.appendChild(input)
        let att = document.createTextNode(atributo);
        label.appendChild(att)

        tab.appendChild(label)
    })
}

/**
 * @param {HTMLElement} tab
 * 
 * @returns {String}
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
 * 
 * @returns {String}
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
