function select_input(input_type) {
    if (input_type === "single") {
        swap_template("single_layer_template")
    } else if (input_type === "multiple") {
        swap_template("multiple_layer_template")
    } else {
        console.log(`unexpected input_type ${input_type}`)
    }
}

function swap_template(id) {
    /** @type {HTMLTemplateElement} */
    let template = document.getElementById(id);
    let new_node = document.importNode(template.content, true);

    /** @type {HTMLDivElement} */
    let dest = document.getElementById("files")

    dest.replaceChildren(new_node)
}

function init() {
    let input_method = document.getElementById("add-building-form")["inputmethod"]
    select_input(input_method.value)
}
