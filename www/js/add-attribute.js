function anadir_atributo() {
    /** @type {HTMLFormElement} */
    let form = document.getElementById("formAddAttribute")
    let form_data = new FormData(form)
    let name = form_data.get("name");
    let display_name = form_data.get("display_name");

    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/map/api/addAttribute", true);
    xhttp.send(form_data)

    let new_li = document.createElement("li")
    new_li.innerText = `${display_name} (${name})`
    document.getElementById("list").appendChild(new_li)

    form.reset()
}
