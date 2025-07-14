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

function deleteColor() {
    /** @type {HTMLTableElement} */
    let color_list = document.getElementById("colors")
    color_list.deleteRow(color_list.rows.length - 1)
}

function editColors() {
    let form_data = new FormData(document.getElementById("edit-colors-form"))

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/updateColors", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirmEditColors()
            } else {
                let error = get_error_string(this) // from error.js
                window.alert(error)
            }
        }
    }
    xhttp.send(form_data)
}

function confirmEditColors() {
    alert("Colors edited") // TODO: Translate
}
