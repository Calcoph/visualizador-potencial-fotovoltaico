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
        error = interpolate(gettext("When accessing %s, %s"), error_json.endpoint, error_json.reason) // TODO: No english
    } catch(err) {
        error = response.statusText
    }
    return interpolate(gettext("Error %s: %s\nNo changes have been made"), response.status, error) // TODO: No english
}
