// --------------------------------------------------
// MAP SETUP
// --------------------------------------------------
const BACKEND = "https://739mb0wj4b.execute-api.us-west-2.amazonaws.com/default";
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
// GEE NIGHT LIGHTS
// --------------------------------------------------
const nightLightsLayer = L.tileLayer(
    `https://earthengine.googleapis.com/v1/projects/newapp-683f4/maps/88f1faba04b54bc4f3f579f64f8e8a80-99d2609d8c7b6f993856bb2ecc6f027d/tiles/{z}/{x}/{y}`,
    { attribution: "GEE | VIIRS Nighttime Lights", opacity: 1 }
);
nightLightsLayer.addTo(map);
// --------------------------------------------------
// STATES
// --------------------------------------------------
let statesGeoJSON = new L.GeoJSON.AJAX("assets/data/geojson/rerickson_2018_us_state_500k.geojson", {
    style: { color: 'gold', weight: 2, fillOpacity: 0.1 },

    onEachFeature: (feature, layer) => {

        const leafletCenter = layer.getBounds().getCenter();
        const centerPoint = turf.point([leafletCenter.lng, leafletCenter.lat]);
        const isInside = turf.booleanPointInPolygon(centerPoint, feature);

        let labelLatLng;
        if (isInside) {
            labelLatLng = leafletCenter;
        } else {
            const insidePoint = turf.pointOnFeature(feature);
            const [lng, lat] = insidePoint.geometry.coordinates;
            labelLatLng = L.latLng(lat, lng);
        }

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

        layer.on("click", () => {
            map.fitBounds(layer.getBounds());
            stateInfoControl.setContent(`
                <b>${feature.properties.alt_title}</b><br>
                <img src="${feature.properties.image}" 
                    style="width:100%;max-width:240px;margin:8px 0;"><br>
                ${feature.properties.description || ""}
            `);
        });
    }
}).addTo(statesLayer);
// --------------------------------------------------
// US CITIES
// --------------------------------------------------
let citiesGeoJSON = new L.GeoJSON.AJAX("assets/data/geojson/usa_major_cities.geojson", {
    pointToLayer: (f, latlng) =>
        L.circleMarker(latlng, cityStyle(f.properties.Type)),
    onEachFeature: (f, layer) =>
        layer.bindPopup(`
            <b>${f.properties.Municipality}</b><br>
            ${f.properties.ST}<br>
            Type: ${f.properties.Type}
        `)
}).addTo(citiesLayer);

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
    const { bdate, edate } = dateSliderControl.getDates();

    const url = `https://aqs.epa.gov/data/api/monitors/byBox?email=${EPA_EMAIL}&key=${EPA_KEY}`
        + `&param=${PARAM}&bdate=${bdate}&edate=${edate}`
        + `&minlat=${b.getSouth()}&maxlat=${b.getNorth()}`
        + `&minlon=${b.getWest()}&maxlon=${b.getEast()}`;

    const res = await fetch(url);
    const json = await res.json();
    if (!json.Data) return;

    epaGeoJSON.clearLayers();
    epaGeoJSON.addData(json.Data.map(m => ({
        type: "Feature",
        geometry: { type: "Point", coordinates: [+m.longitude, +m.latitude] },
        properties: { site: `${m.state_code}-${m.county_code}-${m.site_number}` }
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

    statesGeoJSON.eachLayer(resetStateStyle);

    // ---------------- Cities ----------------
    citiesGeoJSON.eachLayer(l => {
        const type = l.feature.properties.Type;
        const inside = turf.booleanPointInPolygon(l.toGeoJSON(), drawnPolygon);
        l.setStyle(cityStyle(type, inside));
        if (inside) selectedCities.push(l.feature.properties.Municipality);
    });

    // ---------------- Monitors ----------------
    epaGeoJSON.eachLayer(l => {
        const inside = turf.booleanPointInPolygon(l.toGeoJSON(), drawnPolygon);
        l.setStyle(monitorStyle(inside));
        if (inside) selectedMonitors.push(l.feature.properties.site);
    });

    // ---------------- States ----------------
    statesGeoJSON.eachLayer(l => {
        if (turf.booleanIntersects(l.toGeoJSON(), drawnPolygon)) {
            l.setStyle({ fillColor: 'orange', fillOpacity: 0.3 });
            statesTouched.push(l.feature.properties.alt_title);
        }
    });
    // Immediate feedback while async calls run
    summaryControl.setContent(`
        <b>Selection Summary</b><br>
        States: ${statesTouched.length}<br>
        Cities: ${selectedCities.length}<br>
        Monitors: ${selectedMonitors.length}<br><br>
        <b>Summarizing Points...</b><br>
    `);

    try {
        // Nighttime Lights
        console.log(JSON.stringify(drawnPolygon.geometry))
        var ntl = await fetch(`${BACKEND}/ntlSummary`, {
            method: "POST",
            body: JSON.stringify(drawnPolygon.geometry),
            headers: { "Content-Type": "application/json" }
        }).then(r => r.json()); // this should return the mean valute of ntl in the polygon

        summaryControl.appendContent(`<br><br>${ntl}`);
        console.log("NTL RETURN: " + ntl)
        // AI Summary
        var aiSummary = await fetch(`${BACKEND}/aiSummary`, {
            method: "POST",
            body: JSON.stringify({
                cities: selectedCities,
                monitors: selectedMonitors,
                states: statesTouched,
                ntlStats: ntl
            }),
            headers: { "Content-Type": "application/json" }
        }).then(r => r.text());
        console.log("AI SUMMARY RETURN: " + aiSummary)
        // Append instead of replace
        summaryControl.appendContent(`<br><br>${aiSummary}`);

    } catch (err) {
        summaryControl.appendContent(`<b>Error generating summary:</b><br>${err.message}`);
    }
});

// --------------------------------------------------
// SUMMARY CONTROL (bottom-left)
// --------------------------------------------------
const SummaryControl = L.Control.extend({
    options: { position: 'bottomleft' },

    onAdd: function () {
        this._div = L.DomUtil.create('div', 'summary-box');
        this._div.innerHTML = '<b>AOI Summary</b><br>Draw a polygon to get started!';
        return this._div;
    },

    setContent: function (html) {
        this._div.innerHTML = html;
    },

    appendContent: function (html) {
        this._div.innerHTML += html;
    }
});

// --------------------------------------------------
// STATE INFO CONTROL (bottom-right)
// --------------------------------------------------
const StateInfoControl = L.Control.extend({
    options: { position: 'bottomright' },

    onAdd: function () {
        this._div = L.DomUtil.create('div', 'stateinfo-box');
        this._div.innerHTML = '<b>State Info</b><br>Click a state.';
        L.DomEvent.disableClickPropagation(this._div);
        return this._div;
    },

    setContent: function (html) {
        this._div.innerHTML = `
            <span class="stateinfo-close" title="Close">&times;</span>
            ${html}
        `;
        this._div.querySelector('.stateinfo-close')
            .addEventListener('click', () => {
                this._div.innerHTML = '<b>State Info</b><br>Click a state.';
                map.setView([36.99914216255409, -109.04537518899879], 6);
            });
    }
});

const stateInfoControl = new StateInfoControl();
const summaryControl = new SummaryControl();
map.addControl(stateInfoControl);
map.addControl(summaryControl);
// --------------------------------------------------
// LAYER CONTROL
// --------------------------------------------------
L.control.layers(null, {
    "US States": statesLayer,
    "Major Cities": citiesLayer,
    "EPA Monitors": epaLayer,
    "Nighttime Lights": nightLightsLayer
}).addTo(map);
// --------------------------------------------------
// DATE SLIDER CONTROL
// --------------------------------------------------
const DateSliderControl = L.Control.extend({
    options: { position: 'topright' },

    onAdd: function () {
        this._div = L.DomUtil.create('div', 'date-slider-box leaflet-bar');
        L.DomEvent.disableClickPropagation(this._div);
        L.DomEvent.disableScrollPropagation(this._div);

        this._months = [];
        for (let y = 2020; y <= 2024; y++) {
            for (let m = 1; m <= 12; m++) {
                this._months.push({ year: y, month: m });
            }
        }

        const max = this._months.length - 1;
        this._startIdx = 0;
        this._endIdx   = max;

        this._div.innerHTML = `
            <b>Date Range</b>
            <div class="slider-track-wrapper">
                <div class="slider-rail"></div>
                <div class="slider-fill" id="sliderFill"></div>
                <input type="range" id="sliderStart" min="0" max="${max}" value="${this._startIdx}">
                <input type="range" id="sliderEnd"   min="0" max="${max}" value="${this._endIdx}">
            </div>
            <div class="date-display">
                <span id="displayStart"></span>
                <span id="displayEnd"></span>
            </div>
        `;

        setTimeout(() => {
            const sliderStart  = document.getElementById('sliderStart');
            const sliderEnd    = document.getElementById('sliderEnd');
            const displayStart = document.getElementById('displayStart');
            const displayEnd   = document.getElementById('displayEnd');
            const fill         = document.getElementById('sliderFill');

            const fmt = idx => {
                const { year, month } = this._months[idx];
                return `${year}-${String(month).padStart(2, '0')}`;
            };

            const update = () => {
                let s = +sliderStart.value;
                let e = +sliderEnd.value;

                if (s > e) sliderStart.value = s = e;
                if (e < s) sliderEnd.value   = e = s;

                this._startIdx = s;
                this._endIdx   = e;

                const pct = v => (v / max) * 100;
                fill.style.left  = `${pct(s)}%`;
                fill.style.width = `${pct(e) - pct(s)}%`;

                displayStart.textContent = fmt(s);
                displayEnd.textContent   = fmt(e);

                triggerMonitorLoad();
            };

            sliderStart.addEventListener('input', update);
            sliderEnd.addEventListener('input', update);
            update();
        }, 0);

        return this._div;
    },

    getDates: function () {
        const s = this._months[this._startIdx];
        const e = this._months[this._endIdx];

        const bdate = `${s.year}${String(s.month).padStart(2,'0')}01`;
        const lastDay = new Date(e.year, e.month, 0).getDate();
        const edate   = `${e.year}${String(e.month).padStart(2,'0')}${lastDay}`;

        return { bdate, edate };
    }
});

const dateSliderControl = new DateSliderControl();
map.addControl(dateSliderControl);

loadEPAMonitorsInView(); // first load — now safe to call