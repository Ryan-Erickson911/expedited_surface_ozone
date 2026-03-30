// --------------------------------------------------
// MAP SETUP
// --------------------------------------------------
const BACKEND = "https://739mb0wj4b.execute-api.us-west-2.amazonaws.com";
const map = L.map('map', {
    center: [36.99914216255409, -109.04537518899879],
    zoom: 6
});
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap'
}).addTo(map);
// --------------------------------------------------
// LAYERS
// --------------------------------------------------
const statesLayer = L.layerGroup().addTo(map);
const citiesLayer = L.layerGroup().addTo(map);
const epaLayer    = L.layerGroup().addTo(map);
const drawnItems  = new L.FeatureGroup().addTo(map);
// --------------------------------------------------
// EPA SETTINGS
// --------------------------------------------------
const EPA_EMAIL = "ryanerickson407@gmail.com";
const EPA_KEY   = "taupecrane93";
const PARAM     = "44201";
// --------------------------------------------------
// STYLE HELPERS
// --------------------------------------------------
function cityBaseColor(type){
    switch(type){
        case "State's largest municipality": return "red";
        case "State capital and largest municipality": return "orange";
        case "State's second largest municipality": return "green";
        case "City": return "blue";
        case "State capital": return "yellow";
        case "Federal capital": return "purple";
        default: return "#999999";
    }
}
function cityStyle(type, selected=false){
    return {
        radius: 5,
        color: "#000",
        fillColor: selected ? "teal" : cityBaseColor(type),
        fillOpacity: 0.9
    };
}
function monitorStyle(selected=false){
    return {
        radius: 4,
        color: "#000",
        fillColor: selected ? "lime" : "red",
        fillOpacity: 0.8
    };
}
function resetStateStyle(layer){
    layer.setStyle({ color:'gold', weight:2, fillOpacity:0.1 });
}
// --------------------------------------------------
// GEE NIGHT LIGHTS (tile layer goes on MAP)
// --------------------------------------------------
const nightLightsLayer = L.tileLayer(
    `https://earthengine.googleapis.com/v1/projects/ryer7052-ee/maps/88f1faba04b54bc4f3f579f64f8e8a80-67858b1b15d58980236c45e2740dd9b6/tiles/{z}/{x}/{y}`,
    { attribution: "GEE | VIIRS Nighttime Lights", opacity: 1 }
);
nightLightsLayer.addTo(map);
// --------------------------------------------------
// STATES
// --------------------------------------------------
let statesGeoJSON;
statesGeoJSON = new L.GeoJSON.AJAX("/data/geojson/rerickson_2018_us_state_500k.geojson", {
    style: { color: 'gold', weight: 2, fillOpacity: 0.1 },

    onEachFeature: (feature, layer) => {

        // Default Leaflet "center"
        const leafletCenter = layer.getBounds().getCenter();
        const centerPoint = turf.point([leafletCenter.lng, leafletCenter.lat]);

        // Check if that point is actually inside the state
        const isInside = turf.booleanPointInPolygon(centerPoint, feature);

        let labelLatLng;

        if (isInside) {
            // Safe to use Leaflet center
            labelLatLng = leafletCenter;
        } else {
            // Use a guaranteed interior point
            const insidePoint = turf.pointOnFeature(feature);
            const [lng, lat] = insidePoint.geometry.coordinates;
            labelLatLng = L.latLng(lat, lng);
        }

        // Invisible marker to anchor the label
        L.marker(labelLatLng, {
            interactive: false,
            opacity: 0
        })
        .addTo(statesLayer)
        .bindTooltip(feature.properties.NAME, {
            permanent: true,
            direction: "center",
            className: "state-label"
        });

        // --- POPUP ---
        layer.bindPopup(
            `<center><b>${feature.properties.alt_title}</b></center><br><br>
             <img src="${feature.properties.image}" style="width:100%;max-width:200px;display:block;margin:8px auto;"><br>
             ${feature.properties.description}`
        );

        layer.on("click", () => map.fitBounds(layer.getBounds()));
    }
}).addTo(statesLayer);
// --------------------------------------------------
// US CITIES
// --------------------------------------------------
let citiesGeoJSON = new L.GeoJSON.AJAX("/data/geojson/usa_major_cities.geojson", {
    pointToLayer: (f, latlng) =>
        L.circleMarker(latlng, cityStyle(f.properties.Type)),
    onEachFeature: (f, layer) =>
        layer.bindPopup(`
            <b>${f.properties.Municipality}</b><br>
            ${f.properties.ST}<br>
            Type: ${f.properties.Type}
        `)
}).addTo(citiesLayer);
citiesGeoJSON.eachLayer(l=>{
    const type = l.feature.properties.Type;
    const inside = turf.booleanPointInPolygon(l.toGeoJSON(), drawnPolygon);
    l.setStyle(cityStyle(type, inside));
    if(inside) selectedCities.push(l.feature.properties.Municipality);
});
// --------------------------------------------------
// EPA MONITORS
// --------------------------------------------------
let epaGeoJSON = L.geoJSON(null, {
    pointToLayer: (feature, latlng) =>
        L.circleMarker(latlng, monitorStyle(false)),
    onEachFeature: (feature, layer) => {
        layer.bindPopup(`Monitor: ${feature.properties.site}`);
    }
}).addTo(epaLayer);
async function loadEPAMonitorsInView() {
    const b = map.getBounds();

    const url = `https://aqs.epa.gov/data/api/monitors/byBox?email=${EPA_EMAIL}&key=${EPA_KEY}`
        + `&param=${PARAM}&bdate=20231201&edate=20231231`
        + `&minlat=${b.getSouth()}&maxlat=${b.getNorth()}`
        + `&minlon=${b.getWest()}&maxlon=${b.getEast()}`;

    const res = await fetch(url);
    const json = await res.json();
    if (!json.Data) return;

    epaGeoJSON.clearLayers();

    epaGeoJSON.addData(json.Data.map(m => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [+m.longitude, +m.latitude] }, 
        properties: {
            site: `${m.state_code}-${m.county_code}-${m.site_number}`    //add more monitor content here
        }
    })));
}
// --------------------------------------------------
// AUTO LOAD + THROTTLE
// --------------------------------------------------
let monitorTimeout;
function triggerMonitorLoad(){
    clearTimeout(monitorTimeout);
    monitorTimeout = setTimeout(loadEPAMonitorsInView, 400);
}
map.on('moveend', triggerMonitorLoad);
loadEPAMonitorsInView(); // first load
// --------------------------------------------------
// DRAW CONTROL
// --------------------------------------------------
map.addControl(new L.Control.Draw({
    edit: { featureGroup: drawnItems },
    draw: { polygon: true, polyline:false, rectangle:false, circle:false, marker:false }
}));
// --------------------------------------------------
// DRAW ANALYSIS
// --------------------------------------------------
map.on(L.Draw.Event.CREATED, async function (event) {

    drawnItems.clearLayers();
    drawnItems.addLayer(event.layer);
    const drawnPolygon = event.layer.toGeoJSON();

    let selectedCities = [];
    let selectedMonitors = [];
    let statesTouched = [];

    // Reset state styles first
    statesGeoJSON.eachLayer(resetStateStyle);

    // Cities
    citiesGeoJSON.eachLayer(l=>{
        let inside = turf.booleanPointInPolygon(l.toGeoJSON(), drawnPolygon);
        l.setStyle(cityStyle(inside));
        if(inside) selectedCities.push(l.feature.properties.Municipality);
    });

    // Monitors
    epaGeoJSON.eachLayer(l=>{
        let inside = turf.booleanPointInPolygon(l.toGeoJSON(), drawnPolygon);
        l.setStyle(monitorStyle(inside));
        if(inside) selectedMonitors.push(l.feature.properties.site);
    });

    // States
    statesGeoJSON.eachLayer(l=>{
        if(turf.booleanIntersects(l.toGeoJSON(), drawnPolygon)){
            l.setStyle({fillColor:'orange', fillOpacity:0.3});
            statesTouched.push(l.feature.properties.alt_title);
        }
    });

    let ntl = await fetch(`${BACKEND}/ntlSummary`, {
        method: "POST",
        body: JSON.stringify(drawnPolygon),
        headers: { "Content-Type": "ai_engine/application/json" }
    }).then(r => r.json());

    let aiSummary = await fetch(`${BACKEND}/aiSummary`, {
        method: "POST",
        body: JSON.stringify({
            cities: selectedCities,
            monitors: selectedMonitors,
            states: statesTouched,
            ntlStats: ntl
        }),
        headers: { "Content-Type": "ai_engine/application/json" }
    }).then(r => r.text());

    L.popup()
        .setLatLng(event.layer.getBounds().getCenter())
        .setContent(aiSummary)
        .openOn(map);
});
// --------------------------------------------------
// LAYER CONTROL
// --------------------------------------------------
L.control.layers(null, {
    "US States": statesLayer,
    "Major Cities": citiesLayer,
    "EPA Monitors": epaLayer,
    "Nighttime Lights": nightLightsLayer
}).addTo(map);