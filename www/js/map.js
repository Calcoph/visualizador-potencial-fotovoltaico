/// <reference path="../../typings/index.d.ts" />

var map = L.map('map').setView([51.505, -0.09], 13);

/* TODO: Read https://operations.osmfoundation.org/policies/tiles/ */
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

var marker = L.marker([51.5, -0.09]).addTo(map);
