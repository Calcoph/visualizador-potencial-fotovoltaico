function attributesChanged() {
    /** @type {HTMLSelectElement} */
    let colorAttribute = document.getElementById("color-attribute-select")

    let selectedColor = undefined
    if (colorAttribute.selectedIndex >= 0) {
        // If there is no selection, slectedIndex is -1
        selectedColor = colorAttribute.selectedOptions[0].value
    }

    recreate_color_select_list(selectedColor)
}

/**
 * Update the list of attribute used to color
 *
 * @param {String} selectedColor The currently selected color
 */
function recreate_color_select_list(selectedColor) {
    /** @type {HTMLSelectElement} */
    let attributes = document.getElementById("attribute-select")
    /** @type {HTMLSelectElement} */
    let colorAttribute = document.getElementById("color-attribute-select")

    // Remove all the (old) options
    let colorOptions = Array.from(colorAttribute.options)
    for (const _ in colorOptions) {
        colorAttribute.options.remove(0)
    }

    // Create all the (new) options
    let colorOptionAmount = 0
    for (const selectedAttribute of Array.from(attributes.selectedOptions)) {
        // Create new option
        let newOption = document.createElement("option")
        newOption.value = selectedAttribute.value
        newOption.innerText = selectedAttribute.innerText
        colorAttribute.append(newOption)

        // Reselect the color
        if (selectedColor !== undefined) {
            if (newOption.value == selectedColor) {
                colorAttribute.selectedIndex = colorOptionAmount
            }
        }

        colorOptionAmount += 1
    }
}
