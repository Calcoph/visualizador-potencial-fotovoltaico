function editAttribute() {
    let form_data = new FormData(document.getElementById("formEditAttribute"))
    let displayName = form_data.get("display_name");
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editAttribute", true);
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                confirm_edit_attribute(displayName)
            } else {
                let error = get_error_string(this) // from error.js
                window.alert(error)
            }
        }
    }
    xhttp.send(form_data)
}

function confirm_edit_attribute(displayName) {
    let titleNameNode = document.getElementById("title_name");
    titleNameNode.innerHTML = displayName
}
