/// <reference path="../../typings/index.d.ts" />

/** @type {Number}  */
const RESOLUTION = 0.1 // Each cunk is 0.3º wide square
/** @type {Array<Chunk>} */
const LOADED_CHUNKS = []
/** @type {L.Map} */
var MAP = null;
/** @type {number} */
const MAX_ZOOMLEVEL = 12
/** @type {boolean} */
var UPDATES_ENABLED = true
/** @type {Object.<string, L.GeoJSON>} */
const LAYERS = {}

function init_map() {
    MAP = L.map('map').setView([43.2629, -2.95], 14);
    /** @type {L.GeoJSON} */

    geojson_layer = L.geoJSON(null, {
        onEachFeature: init_data
    });
    LAYERS["geojson"] = geojson_layer

    geojson_layer.addTo(MAP)
    add_placeholder_data(geojson_layer)

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(MAP);

    //var marker = L.marker([43.2629, -2.95]).addTo(map);

    L.Control.LoadState  = L.Control.extend({
        onAdd: function(map) {
                var img = L.DomUtil.create("img");

                img.id = "loader_svg"
                img.src = "/smap/svg/green.svg";
                img.style.width = "20px";

                return img
        },

        onRemove: function(map) {

        }
    })

    L.control.loadState = function(opts) {
        return new L.Control.LoadState(opts)
    }

    L.control.loadState({ position: "bottomleft" }).addTo(MAP)

    MAP.on("zoom", (event) => update_zoom(MAP, event))
    MAP.on("move", (event) => update_map(MAP, event))
    update_zoom(MAP, null)
    update_map(MAP, null)
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
 * @param {L.GeoJSON} layer
 */
function add_placeholder_data(layer) {
    layer.addData(
        {
            "type": "Feature",
            "properties": {_sum: 1},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-2.942, 43.267],
                    [-2.938, 43.266],
                    [-2.939, 43.264],
                    [-2.944, 43.265]
                ]]
            },
            "mycomment": "adsad"
        },
    )

    layer.addData(
        {
            "type": "Feature",
            "properties": {_sum: 2},
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [-2.942, 43.262],
                    [-2.938, 43.261],
                    [-2.939, 43.259],
                    [-2.944, 43.260]
                ]]
            },
            "mycomment": "adsad"
        }
    )
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
        const found_chunk = LOADED_CHUNKS.find((loaded_chunk) => {
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

    LOADED_CHUNKS
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
        LOADED_CHUNKS.push(chunk)

        fetch(`/map/api/getPlaceholderData?lat=${chunk.lat}&lon=${chunk.lon}`)
            .then(response => response.json())
            .then((json) => {
                let geojson_layer = LAYERS["geojson"]
                for (datum of json.data) {
                    geojson_layer.addData(datum)
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
    layer.bindPopup(datum.properties._sum.toString())
}
