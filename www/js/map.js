/// <reference path="../../typings/index.d.ts" />

function init_map() {
    var map = L.map('map').setView([43.2629, -2.95], 18);
    
    /* TODO: Read https://operations.osmfoundation.org/policies/tiles/ */
    /* L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map); */
    
    //var marker = L.marker([43.2629, -2.95]).addTo(map);
    
    fetch("./geojson/a.geojson")
        .then(response => response.json())
        .then((json) => {
            L.geoJSON(json).addTo(map)
        })
}
