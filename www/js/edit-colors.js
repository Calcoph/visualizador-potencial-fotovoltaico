function update_color(color) {
    let color_display = color.children.item(1)
    let color_input = color.children.item(2).children.item(0)
    let color_value = color_input.value
    // TODO: More validation
    if (color_value[0] !== "#") {
        color_value = "#" + color_value
        color_input.value = color_value
    }
    color_display.style.backgroundColor = color_value
}

/**
 *
 * @param {HTMLTableRowElement} caller
 */
function swap_color_down(caller) {
    let down_color = caller.nextElementSibling
    if (down_color !== null) {
        swap_colors(caller, down_color)
        update_color(caller)
        update_color(down_color)
    }
}

/**
 *
 * @param {HTMLTableRowElement} caller
 */
function swap_color_up(caller) {
    let up_color = caller.previousElementSibling
    if (up_color !== null) {
        swap_colors(caller, up_color)
        update_color(caller)
        update_color(up_color)
    }
}

function swap_colors(color0, color1) {
    let color0_text_input = color0.children.item(2).children.item(0)
    let color1_text_input = color1.children.item(2).children.item(0)
    let color0_value = color0_text_input.value
    let color1_value = color1_text_input.value

    color0_text_input.value = color1_value
    color1_text_input.value = color0_value
}

init()
