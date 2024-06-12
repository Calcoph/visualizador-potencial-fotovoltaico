/**
 *
 * @param {HTMLTableRowElement} caller
 */
function swap_color_down(caller) {
    let down_color = caller.nextElementSibling
    if (down_color !== null) {
        swap_colors(caller, down_color)
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
    }
}

/**
 *
 * @param {HTMLTableRowElement} color0
 * @param {HTMLTableRowElement} color1
 */
function swap_colors(color0, color1) {
    let color0_input = color0.children[1].children[0]
    let color1_input = color1.children[1].children[0]
    let color0_value = color0_input.value
    let color1_value = color1_input.value

    color0_input.value = color1_value
    color1_input.value = color0_value
}

init()
