function editParameter() {
    let form_data = new FormData(document.getElementById("formEditParameter"))
    let name = form_data.get("name");
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/editParameter", true);
    xhttp.send(form_data)

    let titleNameNode = document.getElementById("title_name");
    titleNameNode.innerHTML = name
}
