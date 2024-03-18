function atributos_cambiados() {
    /** @type {HTMLSelectElement} */
    let atributos = document.getElementById("seleccion-atributo")
    /** @type {HTMLSelectElement} */
    let atributo_color = document.getElementById("seleccion-atributo-color")
    //let color_seleccionado = atributo_color.selectedOptions[0]

    let atributos_seleccionados = Array.from(atributos.selectedOptions)

    let color_seleccionado = undefined
    if (atributo_color.selectedIndex >= 0) {
        // Si no hay ninguno seleccionado, slectedIndex es -1
        color_seleccionado = atributo_color.selectedOptions[0].value
    }

    // Actualizar la lista de posibles atributos que utilizar para colorear
    let opciones_color = Array.from(atributo_color.options)
    for (const _ in opciones_color) {
        atributo_color.options.remove(0)
    }

    let cantidad_opciones_color = 0
    for (const atributo_seleccionado of Array.from(atributos.selectedOptions)) {
        let nueva_opcion = document.createElement("option")
        nueva_opcion.value = atributo_seleccionado.value
        nueva_opcion.innerText = atributo_seleccionado.innerText
        atributo_color.append(nueva_opcion)
        if (color_seleccionado !== undefined) {
            if (nueva_opcion.value == color_seleccionado) {
                atributo_color.selectedIndex = cantidad_opciones_color
            }
        }

        cantidad_opciones_color += 1
    }
}
