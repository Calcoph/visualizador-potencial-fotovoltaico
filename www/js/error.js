/**
* @param {XMLHttpRequest} response
* @returns {String}
*/
function get_error_string(response) {
    var error = "";
    try {
        let error_json = JSON.parse(response.response)
        if (error_json.endpoint === undefined || error_json.reason === undefined) {
            throw "Err"
        }
        error = `When accessing ${error_json.endpoint}, ${error_json.reason}`
    } catch(err) {
        error = response.statusText
    }
    return `Error ${response.status}: ${error}\nNo changes have been made`
}
