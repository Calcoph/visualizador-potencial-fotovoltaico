/// <reference path="../../typings/index.d.ts" />

/** @type {Number}  */
const RESOLUTION = 0.1 // Each cunk is 0.3º wide square
/** @type {Object.<string, Array<Chunk>>} */
var LOADED_CHUNKS = {}
/** @type {L.Map} */
var MAP = null;
/** @type {number} */
const MAX_ZOOMLEVEL = 12
/** @type {boolean} */
var UPDATES_ENABLED = true
/** @type {Object.<string, L.GeoJSON>} */
const LAYERS = {}
/** @type {Array<{display_name: string, name: string}>} */
let SELECTED_ATTRIBUTES = []
/** @type {string} */
let SELECTED_LAYER = undefined
/** @type {{colors: Array<string>, minimums: Object.<string, Array<number>>}} */
const COLOR_SET = {
    colors: [],
    minimums: {}
}
/** @type {Array<number}} */
let CURRENT_MINIMUMS = []

const DEFAULT_COORDS = [43.2629, -2.95];

function init_ui() {
    document.getElementById("legend-loader-close-button").addEventListener("click", function() {
        document.getElementById("legend-loader").close()
    })
}

function init_map() {
    MAP = L.map('map', {
        "crs": L.CRS.EPSG3857 // Just to make sure the default never changes
    }).setView(DEFAULT_COORDS, 14);

    // colorset won't automatically be initialized at this time, have to wait asyc AJAX
    let colorset_promise = init_colorset()
    // layers won't automatically be added at this time, have to wait asyc AJAX
    let layer_promise = add_layers(colorset_promise)

    L.tileLayer('http://localhost:8081/tile/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        referrerPolicy: "origin",
    }).addTo(MAP);

    //var marker = L.marker([43.2629, -2.95]).addTo(map);

    L.Control.LoadState = L.Control.extend({
        onAdd: function(map) {
                var img = L.DomUtil.create("img");

                img.id = "loader_svg"
                img.src = "/smap/svg/green.svg";
                img.style.width = "20px";
                img.addEventListener("click", function() {
                    document.getElementById("legend-loader").showModal()
                })

                return img
        },

        onRemove: function(map) {

        }
    })

    L.control.loadState = function(opts) {
        return new L.Control.LoadState(opts)
    }

    L.control.loadState({ position: "bottomleft" }).addTo(MAP)
}

/**
 *
 * @returns {Promise<any>} promise
 */
function init_colorset() {
    return fetch("/map/api/getColors")
        .then(response => response.json())
        .then((json) => {
            COLOR_SET.colors = json.colors
            COLOR_SET.minimums = json.minimums
        })
}

/**
 *
 * @param {L.Map} map
 * @param {L.Event} event
 */
function update_zoom(map, event) {
    zlevel = MAP.getZoom()
    console.log(`zoom level change: ${zlevel}`)
    if (zlevel < MAX_ZOOMLEVEL) {
        if (UPDATES_ENABLED) {
            // Disable updates
            console.log("Disabling updates")
            UPDATES_ENABLED = false
            var loader_svg = document.getElementById("loader_svg")
            loader_svg.src = "/smap/svg/red.svg"
            loader_svg.title = gettext("No se muestran más edificios, haz zoom para que se empiecen a cargar")
        }
    } else {
        if (!UPDATES_ENABLED) {
            // Enable updates
            console.log("Enabling updates")
            UPDATES_ENABLED = true
            var loader_svg = document.getElementById("loader_svg")
            loader_svg.src = "/smap/svg/green.svg"
            loader_svg.title = gettext("Los edificios han sido cargados")
        }
    }
}

/**
 *
 * @param {L.Map} map
 * @param {L.Event} event
 */
function update_map(map, event) {
    if (UPDATES_ENABLED) {
        console.log("Updating map")

        let bounds = map.getBounds();

        let chunks = get_chunk_list(
            bounds.getNorth(),
            bounds.getSouth(),
            bounds.getEast(),
            bounds.getWest(),
        )

        if (chunks.length == 0) {
            console.log({north,south,east,west})
        }
        update_loaded_chunk_list(chunks)
        load_chunks(chunks)
    }
}

/**
 *
 * @param {L.Map} map
 * @param {L.Event} event
 */
function clamp_map(map, event) {
    center = map.getCenter();
    if (center.lng > 180) {
        console.log("Moved out of bounds. Teleporting")
        long = center.lng - 360
        while (long > 180) {
            long = long - 360
        }
        map.setView([center.lat, long], map.getZoom())
        return;
    }

    if (center.lng < -180) {
        console.log("Moved out of bounds. Teleporting")
        long = center.lng + 360
        while (long < -180) {
            long = long + 360
        }
        map.setView([center.lat, long], map.getZoom())
        return;
    }
}

/**
 * The map is divided in Chunks (their size determined by {@link RESOLUTION}).
 */
class Chunk {
    /**
     *
     * @param {Number} lat latitude
     * @param {Number} lon longitude
     */
    constructor(lat, lon) {
        this.lat = lat
        this.lon = lon
    }

    /**
     *
     * @param {Chunk} chunk
     * @returns {Boolean}
     */
    eq(chunk) {
        return chunk.lat === this.lat && chunk.lon === this.lon
    }
}

/**
 * Given the edges of the map (north, south, east, west),
 *
 * Returns a list of {@link Chunk}. Each chunk is a tile in a grid,
 * The size of each chunk is determined by {@link RESOLUTION}.
 *
 * It is not a list of the exact chunks that appear in screen,
 * some out-of-screen chunks are also inserted to load them before the user
 * pans to that part of the map.
 *
 * @param {Number} north
 * @param {Number} south
 * @param {Number} east
 * @param {Number} west
 * @returns {Array<Chunk>}
 */
function get_chunk_list(north, south, east, west) {
    // Clamp the values, latitude is -90<lat<90, longitude -180<lat<180
    if (north > 90) {
        console.log("clamped north")
        north = 90
    }
    if (south < -90) {
        console.log("clamped south")
        south = -90
    }
    if (east > 180) {
        console.log("clamped east")
        east = 180
    }
    if (west < -180) {
        console.log("clamped west")
        west = -180
    }
    // North is positive, South negative
    // +1 and -1 to load 2 extra rows of chunks
    n = Math.floor(north / RESOLUTION) + 1
    s = Math.floor(south / RESOLUTION) - 1

    // East is positive, West negative
    // +1 and -1 to load 2 extra columns of chunks
    e = Math.floor(east / RESOLUTION) + 1
    w = Math.floor(west / RESOLUTION) - 1

    const chunks_list = []
    for (let lon = s; lon <= n; lon++) {
        for (let lat = w; lat <= e; lat++) {
            chunks_list.push(new Chunk(lat, lon))
        }
    }

    return chunks_list
}

/**
 *
 * @param {Array<Chunk>} chunks list of chunks to be loaded
 * # Mutation
 * mutated values:
 *  * chunks
 *
 * This function mutates the chunks list, to remove the ones that have already been loaded
 */
function update_loaded_chunk_list(chunks) {
    const removing_indices = []
    for ([index, chunk] of chunks.entries()) {
        // find if chunk is in LOADED_CHUNKS
        const found_chunk = LOADED_CHUNKS[SELECTED_LAYER].find((loaded_chunk) => {
            return loaded_chunk.eq(chunk)
        });

        if (found_chunk !== undefined) {
            // chunk is loaded, so it must be removed to not load it again
            removing_indices.push(index)
        }
    }

    for(i of removing_indices.reverse()) {
        chunks.splice(i, 1)
    }
}

/**
 *
 * @param {Array<Chunk>} chunks
 * # Side effects
 * altered values:
 *  * LOADED_CHUNKS
 * This function adds chunks to LOADED_CHUNKS global variable
 */
function load_chunks(chunks) {
    for (chunk of chunks) {
        LOADED_CHUNKS[SELECTED_LAYER].push(chunk)

        fetch(`/map/api/getData?layer=${SELECTED_LAYER}&lat=${chunk.lat}&lon=${chunk.lon}`)
            .then(response => response.json())
            .then((json) => {
                let destination_layer = LAYERS[json.layer]
                for (datum of json.data) {
                    destination_layer.addData(datum)
                }
            })
    }
}

/**
 *
 * @param {any} datum The GeoJSON object
 * @param {L.GeoJSON} layer The GeoJSON layer
 */
function init_data(datum, layer) {
    popup_string = get_popup_content(datum)
    layer.bindPopup(popup_string)
}

function get_popup_content(datum) {
    let popup_string = ""
    for (const attribute of SELECTED_ATTRIBUTES) {
        let properties = datum.properties
        let property = properties[attribute.name]
        if (property) {
            popup_string += attribute.display_name + ": " + property.toString() + "<br>"
        }
    }

    if (!popup_string) {
        popup_string = gettext("Selecciona al menos un atributo")
    }

    return popup_string
}

function update_data_popups() {
    LAYERS[SELECTED_LAYER].eachLayer(function(layer) {
        layer.setPopupContent(get_popup_content(layer.feature))
    })
}

function update_selected_attributes() {
    SELECTED_ATTRIBUTES = []
    let tab_html = document.getElementById("tab");
    for (const child of tab_html.children) {
        let checkbox = child.children[0]
        if (checkbox.checked) {
            SELECTED_ATTRIBUTES.push({
                "name": checkbox.name,
                "display_name": checkbox.value
            })
        }
    }
    update_data_popups()
}

/**
 * @param {Promise<any>} colorset_promise
 * @returns {Promise<any>} promise
 */
function add_layers(colorset_promise) {
    return fetch("api/getLayers")
        .then(response => response.json())
        .then((json) => {
            first_layer = json.layers[0]
            console.assert(SELECTED_LAYER === undefined, "SELECTED_LAYER redefinition")
            SELECTED_LAYER = first_layer.id.toString()
            colorset_promise.then(
                () => {
                    // CURRENT_MINIMUMS must be initialized after SELECTED_LAYER and COLOR_SET, but before estilo() must be called
                    console.assert(COLOR_SET.colors.length > 0, "COLOR_SET sin inicializar")
                    console.assert(SELECTED_LAYER !== undefined, "SELECTED_LAYER sin inicializar")
                    CURRENT_MINIMUMS = COLOR_SET.minimums[SELECTED_LAYER]
                }
            ).then(
                () => {
                    for (const layer of json.layers) {
                        let newLayer = L.geoJSON(null, {
                            onEachFeature: init_data,
                            style: (edificio) => estilo(edificio, layer.color_measure)
                        })

                        id = layer.id.toString()
                        LAYERS[id] = newLayer

                        newLayer.display_name = layer.name
                        newLayer.measures = layer.measures
                        newLayer.color_measure = layer.color_measure
                        LOADED_CHUNKS[id] = []
                        if (id === SELECTED_LAYER) {
                            on_first_layer_loaded()
                            newLayer.addTo(MAP)
                        }
                    }
                    refrescar_tab()
            })
        })
}

function on_first_layer_loaded() {
    on_layer_loaded()

    MAP.on("zoom", (event) => update_zoom(MAP, event))
    MAP.on("move", (event) => update_map(MAP, event))
    MAP.on("moveend", (event) => clamp_map(MAP, event))
}

function on_layer_loaded() {
    overwrite_selected_attributes()
    overwrite_legend()
    update_zoom(MAP, null)
    update_map(MAP, null)
}

function overwrite_selected_attributes() {
    SELECTED_ATTRIBUTES = LAYERS[SELECTED_LAYER].measures
    refrescar_tab()
}

function overwrite_legend() {
    /** @type {HTMLTableElement} */
    const legend = document.getElementById("color-legend")
    for (const i in CURRENT_MINIMUMS) {
        const minimum = CURRENT_MINIMUMS[i];
        legend.rows[i].children[1].textContent = minimum
    }
}

function cambiar_capa(layerName) {
    let oldLayer = LAYERS[SELECTED_LAYER]
    oldLayer.removeFrom(MAP)
    SELECTED_LAYER = layerName
    CURRENT_MINIMUMS = COLOR_SET.minimums[SELECTED_LAYER]
    let newLayer = LAYERS[SELECTED_LAYER]
    newLayer.addTo(MAP)

    on_layer_loaded()
}

function calculateColor(d) {
    // CURRENT_MINIMUMS must be initialized before calling calculateColor
    console.assert(CURRENT_MINIMUMS.length > 0, "CURRENT_MINIMUMS sin inicializar")
    let color = COLOR_SET.colors[COLOR_SET.colors.length-1] // Por defecto el color es el último.
    for (const i in CURRENT_MINIMUMS) {
        const minimum = CURRENT_MINIMUMS[i];
        if (d > minimum) {
            color = COLOR_SET.colors[i]
            break
        }
    }
    return color;
}

function estilo(edificio, propiedad) {
    return {
        fillColor: calculateColor(edificio.properties[propiedad]),
        weight: 1,
        color: "#000000",
        fillOpacity: 0.6
    }
}
