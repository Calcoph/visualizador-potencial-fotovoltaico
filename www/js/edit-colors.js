const DEFAULT_COLOR = "#000000"

function anadir_color() {
    let colores = document.getElementById("colores")
    // <tr>
    let row = document.createElement("tr")
    let row_id = COLOR_AMOUNT
    row.id = `color_${row_id}`

    //     <td>
    let move_buttons = document.createElement("td")
    let button_up = document.createElement("input")
    button_up.type = "button"
    button_up.value = "↑"
    button_up.onclick = function() {swap_color_up(row_id)}

    let button_down = document.createElement("input")
    button_down.type = "button"
    button_down.value = "↓"
    button_down.onclick = function() {swap_color_down(row_id)}

    let br = document.createElement("br")
    move_buttons.appendChild(button_up)
    move_buttons.appendChild(br)
    move_buttons.appendChild(button_down)
    //     </td>

    //     <td>
    let color = document.createElement("td")
    color.style = `width:50px;height:50px;background-color:${DEFAULT_COLOR};border:1px solid black`
    //     </td>

    //     <td>
    let input_color_td = document.createElement("td")
    let input_color = document.createElement("input")
    input_color.type = "text"
    input_color.name = "color"
    input_color.value = DEFAULT_COLOR
    input_color.onchange = function() {update_color(row_id)}
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
    console.log(index)
    let color = document.getElementById(`color_${index}`)
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

function init() {
    let colores = document.getElementById("colores")
    COLOR_AMOUNT = colores.children.length
}

function swap_color_down(index) {
    console.log(index)
    let color = document.getElementById(`color_${index}`)
    let down_color = document.getElementById(`color_${index+1}`)
    if (down_color !== null) {
        swap_colors(color, down_color)
        update_color(index)
        update_color(index+1)
    }
}

function swap_color_up(index) {
    console.log(index)
    let color = document.getElementById(`color_${index}`)
    let up_color = document.getElementById(`color_${index-1}`)
    if (up_color !== null) {
        swap_colors(color, up_color)
        update_color(index)
        update_color(index-1)
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
