const ee = require('@google/earthengine');

async function initEE() {
    return new Promise((resolve, reject) => {
        ee.data.authenticateViaPrivateKey({
            client_email: process.env.GEE_SERVICE_ACCOUNT,
            private_key: process.env.GEE_PRIVATE_KEY,
        }, () => {
            ee.initialize(null, null, resolve, reject);
        }, reject);
    });
}

async function ntlSummary(polygonGeoJSON) {
    await initEE();

    const geom = ee.Geometry(polygonGeoJSON.geometry);

    const ntl = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")
        .filterDate('2023-12-01', '2023-12-31')
        .select('avg_rad')
        .mean();

    const stats = ntl.reduceRegion({
        reducer: ee.Reducer.mean()
            .combine(ee.Reducer.min(), '', true)
            .combine(ee.Reducer.max(), '', true)
            .combine(ee.Reducer.sum(), '', true),
        geometry: geom,
        scale: 500,
        maxPixels: 1e9
    });

    return await stats.getInfo();
}

module.exports = { ntlSummary };