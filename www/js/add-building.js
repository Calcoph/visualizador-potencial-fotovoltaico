function select_input(input_type) {
    let files_html = document.getElementById("files")
    files_html.innerHTML = ""
    if (input_type === "single") {
        files_single(files_html)
    } else if (input_type === "multiple") {
        files_multiple(files_html)
    } else {
        console.log(`unexpected input_type ${input_type}`)
    }
}

function files_single(files) {
    let file_types = ["prj", "dbf", "shx", "shp"]
    for (const file_type of file_types) {
         let label = document.createElement("label")
         let label_text = document.createTextNode("." + file_type)
         label.appendChild(label_text)
         let input = document.createElement("input")
         input.type = "file"
         input.name = file_type
         label.appendChild(input)
         files.appendChild(label)
    }
}

function files_multiple(files) {
    let label = document.createElement("label")
    let label_text = document.createTextNode("Ficheros (.shp, .shx, .dbf y .prj)")
    label.appendChild(label_text)
    let input = document.createElement("input")
    input.type = "file"
    input.name = "multiple_files"
    input.multiple = "multiple"
    label.appendChild(input)
    files.appendChild(label)
}

function init() {
    let input_method = document.getElementById("add-building-form")["inputmethod"]
    select_input(input_method.value)
}

init()
