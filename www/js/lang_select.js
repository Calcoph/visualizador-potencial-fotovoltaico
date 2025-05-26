/**
 *
 * @param {String} lang
 */
function select_lang(lang) {
    let expire_days = 30;
    const d = new Date();
    d.setTime(d.getTime() + (expire_days*24*60*60*1000));
    let expires = d.toUTCString();

    document.cookie = `django_language=${lang}; expires=${expires}; path=/`
    location.reload()
}
