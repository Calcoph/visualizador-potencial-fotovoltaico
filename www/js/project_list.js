function getCookie(cname) {
    return document.cookie
        .split("; ")
        .find(
            (row) => row.startsWith(cname+"=")
        )
        ?.split("=")[1];
}

function select_project(id) {
    redirect = getCookie("project-list-source")

    let xhttp = new XMLHttpRequest()

    xhttp.open("POST", "/map/api/selectProject", false) // synchronous request. Don't redirect until it has been completed
    xhttp.setRequestHeader("content-type", "application/x-www-form-urlencoded")
    let params = "project_id=" + id
    xhttp.send(params)
    if (xhttp.status != 200) {
        return
    }

    if (redirect) {
        if (redirect[0] == '"') {
            redirect = redirect.slice(1, -1) // remove wrapping "
        }
        window.location.href = redirect
    } else {
        window.location.href = "/"
    }
}
