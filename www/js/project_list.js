function select_project(id) {
    let redirect = document.getElementById("next").value
    let xhttp = new XMLHttpRequest()

    xhttp.open("POST", "/map/api/selectProject", false) // synchronous request. Don't redirect until it has been completed
    xhttp.setRequestHeader("content-type", "application/x-www-form-urlencoded")
    let params = "project_id=" + id
    xhttp.send(params)
    if (xhttp.status != 200) {
        window.alert(`No se ha podido cambiar el proyecto por un error inesperado.\n${xhttp.status}: ${xhttp.statusText}`)
        return
    }

    if (redirect) {
        window.location.href = redirect
    } else {
        window.location.href = "/"
    }
}
