const map = L.map('map', {
    center: [38.6359, -95.4835],
    zoom: 5
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
}).addTo(map);

// Click popup
map.on('click', e => {
    L.popup()
        .setLatLng(e.latlng)
        .setContent(`You clicked ${e.latlng.toString()}`)
        .openOn(map);
});

// -----------------------------
// LAYER GROUPS (important for control)
// -----------------------------
const statesLayer = L.layerGroup();
const citiesLayer = L.layerGroup();
const epaLayer    = L.layerGroup();
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

let citiesGeoJSON;   // add above
let epaGeoJSON;      // add above
// -----------------------------
// STATES GEOJSON
// -----------------------------
const states = new L.GeoJSON.AJAX("/data/geojson/rerickson_2018_us_state_500k.geojson", {
    style: {
        color: 'gold',
        weight: 2,
        fillColor: '#ffffff',
        fillOpacity: 0.1
    },
    onEachFeature: (feature, layer) => {
        layer.bindPopup(`
            <center><b>${feature.properties.alt_title}</b></center>
            <img src="${feature.properties.image}" style="width:100%;max-width:200px;margin:8px auto;display:block;">
            ${feature.properties.description}
        `);

        layer.on("click", () => {
            map.fitBounds(layer.getBounds());
        });
    }
}).addTo(statesLayer);

// -----------------------------
// CITIES GEOJSON
// -----------------------------
citiesGeoJSON = new L.GeoJSON.AJAX("/data/geojson/usa_major_cities.geojson", {
    pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, {
            radius: 5,
            color: "#000",
            weight: 1,
            fillOpacity: 0.9
        });
    },
    onEachFeature: (feature, layer) => {
        layer.bindPopup(`
            <b>${feature.properties.Municipality}</b><br>
            ${feature.properties.ST}
        `);
    }
}).addTo(citiesLayer);

// -----------------------------
// EPA MONITORS
// -----------------------------
const EPA_EMAIL = "ryanerickson407@gmail.com";
const EPA_KEY   = "taupecrane93";
const PARAM     = "44201";  // Ozone
const STATE     = "04";     // Arizona

async function loadEPAMonitors() {
    const url = `https://aqs.epa.gov/data/api/monitors/byState?email=${EPA_EMAIL}&key=${EPA_KEY}&param=${PARAM}&bdate=20231201&edate=20231231&state=${STATE}`;

    const res = await fetch(url);
    const json = await res.json();

    if (!json.Data) {
        console.error("EPA response error:", json);
        return;
    }

    const geojson = {
        type: "FeatureCollection",
        features: json.Data.map(m => ({
            type: "Feature",
            geometry: {
                type: "Point",
                coordinates: [+m.longitude, +m.latitude]
            },
            properties: {
                site: `${m.state_code}-${m.county_code}-${m.site_number}`,
                parameter: m.parameter_name,
                agency: m.monitoring_agency,
                last_change: m.date_of_last_change,
                units: m.units_of_measure,
                measurement: m.sample_measurement,
                state: m.state,
                county: m.county,
                elevation: m.elevation
            }
        }))
    };
    const drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polyline: false,
            rectangle: false,
            circle: false,
            marker: false,
            circlemarker: false,
            polygon: {
                allowIntersection: false,
                showArea: true
            }
        }
    });

    map.addControl(drawControl);

    epaGeoJSON = L.geoJSON(geojson, {
        pointToLayer: (feature, latlng) => {
            return L.circleMarker(latlng, {
                radius: 4,
                fillColor: "#ff0000",
                color: "#000",
                weight: 1,
                fillOpacity: 0.8
            });
        },
        onEachFeature: (feature, layer) => {
            const p = feature.properties;
            layer.bindPopup(`
                <b>${p.county}, ${p.state}</b><br>
                Measurement: ${p.measurement} ${p.units}<br>
                Last Update: ${p.last_change}<br>
                Site: ${p.site}<br>
                Parameter: ${p.parameter}<br>
                Agency: ${p.agency}<br>
                Elevation: ${p.elevation} m
            `);
        }
    }).addTo(epaLayer);
}

loadEPAMonitors();

// -----------------------------
// ADD LAYERS TO MAP
// -----------------------------
statesLayer.addTo(map);
citiesLayer.addTo(map);
epaLayer.addTo(map);

// -----------------------------
// LAYER CONTROL (top right)
// -----------------------------
L.control.layers(null, {
    "US States": statesLayer,
    "Major Cities": citiesLayer,
    "EPA Monitors": epaLayer
}).addTo(map);

map.on(L.Draw.Event.CREATED, function (event) {

    const layer = event.layer;
    drawnItems.clearLayers();   // only allow one polygon at a time
    drawnItems.addLayer(layer);

    const drawnPolygon = layer.toGeoJSON();

    let selectedCities = [];
    let selectedMonitors = [];

    // ---- Check Cities ----
    citiesGeoJSON.eachLayer(l => {
        const pt = l.toGeoJSON();
        if (turf.booleanPointInPolygon(pt, drawnPolygon)) {
            l.setStyle({ fillColor: 'yellow' });
            selectedCities.push(l.feature.properties.Municipality);
        }
    });

    // ---- Check EPA Monitors ----
    epaGeoJSON.eachLayer(l => {
        const pt = l.toGeoJSON();
        if (turf.booleanPointInPolygon(pt, drawnPolygon)) {
            l.setStyle({ fillColor: 'lime' });
            selectedMonitors.push(l.feature.properties.site);
        }
    });

    // ---- Summary Popup ----
    L.popup()
        .setLatLng(layer.getBounds().getCenter())
        .setContent(`
            <b>Selection Summary</b><br>
            Cities Selected: ${selectedCities.length}<br>
            Monitors Selected: ${selectedMonitors.length}
        `)
        .openOn(map);
});