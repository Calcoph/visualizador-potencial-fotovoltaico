const DEFAULT_COLOR = "#000"

function anadir_color() {
    let colores = document.getElementById("colores")
    // <tr>
    let row = document.createElement("tr")
    row.id = `color_${COLOR_AMOUNT}`

    // <td>
    let move_buttons = document.createElement("td")
    let button_up = document.createElement("input")
    button_up.type = "button"
    button_up.value = "^"
    let button_down = document.createElement("input")
    button_down.type = "button"
    button_down.value = "v"
    let br = document.createElement("br")
    move_buttons.appendChild(button_up)
    move_buttons.appendChild(br)
    move_buttons.appendChild(button_down)
    // </td>

    // <td>
    let color = document.createElement("td")
    color.style = `width:50px;height:50px;background-color:${DEFAULT_COLOR}`
    // </td>

    // <td>
    let input_color_td = document.createElement("td")
    let input_color = document.createElement("input")
    input_color.type = "text"
    input_color.value = DEFAULT_COLOR
    // TODO: .onchange doesn't work as expected
    input_color.onchange = function () {update_color(COLOR_AMOUNT)}
    input_color_td.appendChild(input_color)

    row.appendChild(move_buttons)
    row.append(color)
    row.append(input_color_td)
    // </tr>
    colores.appendChild(row)

    COLOR_AMOUNT += 1
}

var COLOR_AMOUNT = undefined

function update_color(index) {
    let color = document.getElementById(`color_${index}`).children.item(index)
    let color_display = color.children.item(1)
    let color_value = color.children.item(2).value
    // TODO: More validation
    if (color_value[0] !== "#") {
        color_value = "#" + color_value
        color.children.item(2).value = color_value
    }
    color_display.style.backgroundColor = color_value
}

function init() {
    let colores = document.getElementById("colores")
    COLOR_AMOUNT = colores.children.length
}

init()
