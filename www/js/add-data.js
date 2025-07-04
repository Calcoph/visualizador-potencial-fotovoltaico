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
    let input_method = document.getElementById("add-data-form")["inputmethod"]
    select_input(input_method.value)
}

function submitData() {
    let form_data = new FormData(document.getElementById("add-data-form"))
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/addData", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirmSubmitData(this.response)
            } else {
                document.getElementById("lastLayerResults").innerText = ""
                let error = get_error_string(this)
                window.alert(error)
            }
        }
    }
    xhttp.send(form_data)
}

function confirmSubmitData(response) {
    document.getElementById("lastLayerResults").innerText = "Automatically selected layers:\n" + response // TODO: Translate
    alert("Datos Añadidos") // TODO: Translate
}
