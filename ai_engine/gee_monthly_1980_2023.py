import geemap
import ee
import os
from datetime import datetime, timedelta

# This script gathers the necessary raster data from Google Earth Engine (GEE). This will be used in the extraction and model output process.
ee.Authenticate(auth_mode='localhost')
ee.Initialize(project='ryer7052-ee')
washington = ee.FeatureCollection("projects/ryer7052-ee/assets/wa_state")
wash = washington.union()
# A function to produce a list of date ranges in the format necessary for http communication. 
def get_monthly_intervals(start_date, end_date): #sets intervals for imagery 
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    intervals = []
    current = start
    while current <= end:
        year = current.year
        month = current.month
        first_day = datetime(year, month, 1)
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        intervals.append([first_day.strftime('%Y-%m-%d'), next_month.strftime('%Y-%m-%d')])
        current = next_month
    return intervals
# Export paths for final prediction grid and tif data
tif_path = os.path.join(os.path.expanduser('~'),'Documents','Github','surface_ozone','data','tifs')
grid_path = os.path.join(tif_path, 'p_grd')
elevation = os.path.join(tif_path,'elevation')
lulc = os.path.join(tif_path,'landuseandlandcover')
monthly_gmet = os.path.join(tif_path,'gridmet','monthly')
monthly_oz = os.path.join(tif_path,'ozone10km','monthly')
monthly_ccnl_daynight = os.path.join(tif_path,'ccnl','monthly')
monthly_daynight = os.path.join(tif_path,'viirs','monthly')
monthly_ndvi = os.path.join(tif_path,'ndvi','monthly')
monthly_s5p = os.path.join(tif_path,'s5p','monthly')
monthly_aerosols = os.path.join(tif_path,'aerosols','monthly')
monthly_no2 = os.path.join(tif_path,'no2','monthly')
monthly_hcho = os.path.join(tif_path,'hcho','monthly')
monthly_clouds = os.path.join(tif_path,'clouds','monthly')
monthly_population_density = os.path.join(tif_path,'population_density','monthly')
# GEE Imagery and links to data
# Elevation: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30
# 30M Res
# T: 2010-12-01, 2015-01-31 -> Using 2015-01
if not os.path.exists(elevation):
    os.makedirs(elevation)
    print("Created Monthly GRIDMet Collection folder")
elev_col=(ee.ImageCollection('COPERNICUS/DEM/GLO30').select(['DEM'],['elevation']).mean())
geemap.ee_export_image(elev_col,os.path.join(elevation,f'elevation.tif'),region=wash.geometry(),scale=200,crs='EPSG:4326')
print("Finished with Elevation Export")

# Land Use Land Cover (LULC) https://developers.google.com/earth-engine/datasets/catalog/USGS_NLCD_RELEASES_2020_REL_NALCMS
# 30M Res
# T: 2010-12-01, 2015-01-31 -> Using 2015-01
if not os.path.exists(lulc):
    os.makedirs(lulc)
    print("Created Monthly LULC Collection folder")
lulc_col=(ee.Image('USGS/NLCD_RELEASES/2020_REL/NALCMS'))
geemap.ee_export_image(lulc_col,os.path.join(lulc,f'lulc.tif'),region=wash.geometry(),scale=100,crs='EPSG:4326')
print("Finished with LULC Export")

# GRIDMET: https://developers.google.com/earth-engine/datasets/catalog/IDAHO_EPSCOR_GRIDMET#bands
# 4638.3M Res -> reduced to 500m
# T: 1979-01-01, 2024-09-15 -> 530 files
if not os.path.exists(monthly_gmet):
    os.makedirs(monthly_gmet)
    print("Created Monthly GRIDMet Collection folder")
if len(os.listdir(monthly_gmet))<500:
    intervals=get_monthly_intervals('1980-01-01','2024-01-01')
    for start, end in intervals:
        print(f'{start},{end}')
        main_gm_col=(ee.ImageCollection('IDAHO_EPSCOR/GRIDMET').select(['pr','sph','srad','tmmx','vs','bi','vpd'],['precip','spf_hmdty','down_srad','temp_ax','wdsp','bnid','vprps_def']).filterDate(start,end).mean())
        geemap.ee_export_image(main_gm_col,os.path.join(monthly_gmet,f'gmet_{start}.tif'),region=wash.geometry(),scale=500,crs='EPSG:4326')
    print("Finished with GRIDMet Collection Export")
else:
    print(f"Files detected in {monthly_gmet} and has {len(os.listdir(monthly_gmet))} files in it")
# 10KM Ozone: https://developers.google.com/earth-engine/datasets/catalog/TOMS_MERGED
# 1978-11-01, 2024-09-16
# 111000 meters -> reduced to 500m -> 529 files
if not os.path.exists(monthly_oz):
    os.makedirs(monthly_oz)
    print("Created Monthly TOMS-OMI Merged Ozone folder")
if len(os.listdir(monthly_oz))<500:
    intervals=get_monthly_intervals('1980-01-01','2024-01-01')
    for start, end in intervals:
        ozone10km=(ee.ImageCollection('TOMS/MERGED').select(['ozone']).filterDate(start,end).mean())
        geemap.ee_export_image(ozone10km,os.path.join(monthly_oz,f'toms-omi_oz_{start}.tif'),region=wash.geometry(),scale=250,crs='EPSG:4326')
    print("Finished with monthly TOMS-OMI Merged Ozone Export")    
else:
    print(f"Files detected in {monthly_oz} and has {len(os.listdir(monthly_oz))} files in it")
# DAYNIGHT:https://developers.google.com/earth-engine/datasets/catalog/NOAA_VIIRS_001_VNP46A2
# 2012-01-19, 2024-09-09: 500 meters -> All months avaliable 145 files printed
# Corrected nighttime light intensity:https://developers.google.com/earth-engine/datasets/catalog/BNU_FGS_CCNL_v1
# 1992-01-01, 2014-01-01: 1000 meters -> exported at 500m -> only annual avaliable
if not os.path.exists(monthly_ccnl_daynight):
    os.makedirs(monthly_ccnl_daynight)
    print("Created Monthly Corrected CNL Collection folder")
if len(os.listdir(monthly_ccnl_daynight))<20:
    temp_int=get_monthly_intervals("1992-01-01","2014-01-01")
    for start, end in temp_int:
        daynight_ccnl = (ee.ImageCollection("BNU/FGS/CCNL/v1").select(['b1'],['ccnl_ntl']).filterDate(start, end).mean())
        geemap.ee_export_image(daynight_ccnl,os.path.join(monthly_ccnl_daynight, f'ccntl_{start}.tif'),region = wash.geometry(),scale = 500,crs= 'EPSG:4326')
    print("Finished with monthly NOAA-VIIRS night-time lights collection export")
print(f"Files detected in {monthly_ccnl_daynight} and has {len(os.listdir(monthly_ccnl_daynight))} files in it")
if not os.path.exists(monthly_daynight):
    os.makedirs(monthly_daynight)
    print("Created Monthly VIIRS Collection folder")
if len(os.listdir(monthly_daynight))<140:
    time=get_monthly_intervals("2012-01-19","2024-01-01")
    for start, end in time:
        daynight_viirs = (ee.ImageCollection("NOAA/VIIRS/001/VNP46A2").select(['DNB_BRDF_Corrected_NTL'],['ntl_corrected']).filterDate(start, end).mean())
        geemap.ee_export_image(daynight_viirs,os.path.join(monthly_daynight,f'viirs_ntl_{start}.tif'),region=wash.geometry(),scale=500,crs='EPSG:4326')
    print("Finished with NOAA-VIIRS night time lights collection export")
else:
    print(f"Files detected in {monthly_daynight} and has {len(os.listdir(monthly_daynight))} files in it")
# NDVI -> 677 files -> overlap
# 1981-07-01 2013-12-16: 9277m: ee.ImageCollection("NASA/GIMMS/3GV0"): exported at 5000m
# 2000-02-18 2024-09-13:  250m: ee.ImageCollection("MODIS/061/MOD13Q1"): exported at 50m
if not os.path.exists(monthly_ndvi):
    os.makedirs(monthly_ndvi)
    print("Created Monthly NASA NDVI Collection folder")
if len(os.listdir(monthly_ndvi))<500:
    old_nvdi_ints=get_monthly_intervals("1981-07-01","2013-12-16")
    for start, end in old_nvdi_ints:
        old_ndvi_col=(ee.ImageCollection("NASA/GIMMS/3GV0").select(['ndvi']).filterDate(start, end).mean())
        geemap.ee_export_image(old_ndvi_col,os.path.join(monthly_ndvi,f'ndvi_nasa_{start}.tif'),region = wash.geometry(),scale=500,crs='EPSG:4326')
    print("Finished with Monthly NASA NDVI Export")
    new_intervals=get_monthly_intervals('2000-02-18','2024-01-01')
    for start, end in new_intervals:
        ndvi_col=(ee.ImageCollection("MODIS/061/MOD13Q1").select(['NDVI'],['ndvi']).filterDate(start, end).mean())
        geemap.ee_export_image(ndvi_col,os.path.join(monthly_ndvi,f'ndvi_modis_{start}.tif'),region = wash.geometry(),scale=500,crs='EPSG:4326')
    print("Finished with Monthly MODIS NDVI Export")
else:
    print(f"Files detected in {monthly_ndvi} and has {len(os.listdir(monthly_ndvi))} files in it")
# Sentinal 5P - 1km Ozone -> 677 files
#  2024-10-18 - Current
if not os.path.exists(monthly_s5p):
    os.makedirs(monthly_s5p)
    print("Created Monthly Sentinal 5P Ozone folder")
if len(os.listdir(monthly_s5p))<50:
    intervals=get_monthly_intervals('2018-10-01','2024-01-01')
    for start, end in intervals:
        s5p_ozone1km=(ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_O3').select(['O3_column_number_density','O3_effective_temperature','cloud_fraction'],['tco_nd','tco_temp','cld_fr']).filterDate(start,end).mean())
        geemap.ee_export_image(s5p_ozone1km,os.path.join(monthly_s5p,f's5p_1km_{start}.tif'),region=wash.geometry(),scale=500,crs='EPSG:4326')
    print("Finished with monthly S5P 1KM Ozone Export")    
else:
    print(f"Files detected in {monthly_s5p} and has {len(os.listdir(monthly_s5p))} files in it")
# Aerosol Index:https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_NRTI_L3_AER_AI
# 2018-07-10 - Current
# 1113.2m
if not os.path.exists(monthly_aerosols):
    os.makedirs(monthly_aerosols)
    print(f"Created Aerosol Collection folder")
if len(os.listdir(monthly_aerosols))<50:
    intervals=get_monthly_intervals('2018-10-01','2024-01-01')
    for start, end in intervals:
        aerosol_col = (ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_AER_AI').select(['absorbing_aerosol_index']).filterDate(start,end).mean())
        geemap.ee_export_image(aerosol_col,filename=(monthly_aerosols+'//'+start+".tif"),region=wash.geometry(),scale=500,crs= 'EPSG:4326')
    print("Finished with Sential 5 Aerosol Collection Export")
else:
    print(f"Files detected in {monthly_aerosols} and has {len(os.listdir(monthly_aerosols))} files in it")
# Nitrogen Dioxide (NO2): https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_NRTI_L3_NO2
# 2018-07-10 - Current
# 1113.2 meters
if not os.path.exists(monthly_no2):
    os.makedirs(monthly_no2)
    print(f"Created NO2 Collection folder")
if len(os.listdir(monthly_no2))<50:
    intervals=get_monthly_intervals('2018-10-01','2024-01-01')
    for start, end in intervals:
        no2_col = (ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2').select(['NO2_column_number_density','stratospheric_NO2_column_number_density']).filterDate(start,end).mean())
        geemap.ee_export_image(no2_col,filename=(monthly_no2+'//'+start+".tif"),region=wash.geometry(),scale=500,crs='EPSG:4326')
    print("Finished with Sential 5 NO2 Collection Export")
else:
    print(f"Files detected in {monthly_no2} and has {len(os.listdir(monthly_no2))} files in it")
# Formaldehyde concentrations:https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_NRTI_L3_HCHO
# 2018-10-02::2024-10-29
# 1113.2m
if not os.path.exists(monthly_hcho):
    os.makedirs(monthly_hcho)
    print(f"Created Formaldehyde Collection folder")
if len(os.listdir(monthly_hcho))<50:
    intervals=get_monthly_intervals('2018-10-02','2024-01-01')
    for start, end in intervals:
        hcho_col = (ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_HCHO").select(['tropospheric_HCHO_column_number_density']).filterDate(start,end).mean())
        geemap.ee_export_image(hcho_col,filename=(monthly_hcho+'//'+start+".tif"),region=wash.geometry(),scale=500,crs= 'EPSG:4326')
    print("Finished with Sential 5 Formaldehyde Collection Export")
else:
    print(f"Files detected in {monthly_hcho} and has {len(os.listdir(monthly_hcho))} files in it")
# Clouds:https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_NRTI_L3_CLOUD#bands
# 2018-07-05 - Current 
# 1113.2 m
if not os.path.exists(monthly_clouds):
    os.makedirs(monthly_clouds)
    print(f"Created Sental 5p Cloud Collection folder")
if len(os.listdir(monthly_clouds))<50:
    intervals=get_monthly_intervals('2018-10-01','2024-01-01')
    for start, end in intervals:
        cloud_col = (ee.ImageCollection("COPERNICUS/S5P/NRTI/L3_CLOUD").select(['cloud_fraction','cloud_top_pressure','cloud_top_height','cloud_base_pressure','cloud_base_height','cloud_optical_depth']).filterDate(start,end).mean())
        cloud_col = cloud_col.toFloat()
        change_in_pressure = cloud_col.select('cloud_base_pressure').subtract(cloud_col.select('cloud_top_pressure')).multiply(cloud_col.select(['cloud_fraction'])).rename('change_in_pressure')
        change_in_height = cloud_col.select('cloud_top_height').subtract(cloud_col.select('cloud_base_height')).multiply(cloud_col.select(['cloud_fraction'])).rename('cloud_volume')
        cloud_col = cloud_col.addBands(change_in_pressure).addBands(change_in_height)
        band_product = cloud_col.select(['change_in_pressure','cloud_volume']).reduce(ee.Reducer.mean()).rename('start_index')
        cloud_col = cloud_col.addBands(band_product)
        final = cloud_col.select(['change_in_pressure']).subtract(cloud_col.select(['cloud_volume'])).divide(cloud_col.select(['cloud_volume']).add(cloud_col.select(['change_in_pressure']))).multiply(cloud_col.select(['cloud_optical_depth'])).rename('cloud_index')
        cloud_col = cloud_col.addBands(final)
        cloud_col=cloud_col.select(['cloud_index'])
        geemap.ee_export_image(cloud_col,filename=os.path.join(monthly_clouds,f"{start}.tif"),region=wash.geometry(),scale=500,crs='EPSG:4326')
    print("Finished with Cloud Index Collection Export")
else:
    print(f"Files detected in {monthly_clouds} and has {len(os.listdir(monthly_clouds))} files in it")
if not os.path.exists(monthly_population_density):
    os.makedirs(monthly_population_density)
    print(f"Created Population Density Collection folder")
if len(os.listdir(monthly_population_density))<1:
    intervals=get_monthly_intervals('2018-10-01','2024-01-01')
    for start, end in intervals:
        pop_col = ee.ImageCollection("CIESIN/GPWv411/GPW_Population_Density").select(['population_density']).filterDate(start,end).mean()
        geemap.ee_export_image(pop_col,filename=os.path.join(monthly_population_density,f"popden_{start}.tif"),region=wash.geometry(),scale=150,crs='EPSG:4326')
    print("Finished with Pop Den Collection Export")
else:
    print(f"Files detected in {monthly_population_density} and has {len(os.listdir(monthly_population_density))} files in it")
# creating and exporting 250m empty grid for each date
geometry = wash.geometry()
grid_size = 150
grid_poly = geometry.coveringGrid('EPSG:4326',grid_size)
if not os.path.exists(grid_path):
    os.makedirs(grid_path)
if len(os.listdir(grid_path))<50:
    grid_image = ee.Image().paint(grid_poly, 1, 0.5).rename("wash_grid")
    intervals=get_monthly_intervals('2018-10-01','2024-01-01')
    for start, end in intervals:
        geemap.ee_export_image(grid_image,filename=os.path.join(grid_path,f"wash_grid_{start}.tif"),region=geometry,scale=250,crs='EPSG:4326')  
else:
    print('Exported empty prediction rasters')  
roads = ee.FeatureCollection("TIGER/2016/Roads").filterBounds(wash)
roadRaster = roads.reduceToImage(['FULLNAME'], ee.Reducer.countDistinct()).gt(0)
euclideanKernel = ee.Kernel.euclidean(12500, 'meters')
distanceToRoads = roadRaster.distance(euclideanKernel)
road_path = os.path.join(grid_path, "distance_to_roads.tif")
geemap.ee_export_image(distanceToRoads, filename=road_path, region=geometry, scale=grid_size, crs='EPSG:4326')
print(f"Distance to roads raster exported to {road_path}")
########### Final File Check
print(f'Files in {monthly_gmet}: {len(os.listdir(monthly_gmet))}')
print(f'Files in {monthly_oz}: {len(os.listdir(monthly_oz))}')
print(f'Files in {monthly_ccnl_daynight}: {len(os.listdir(monthly_ccnl_daynight))}')
print(f'Files in {monthly_daynight}: {len(os.listdir(monthly_daynight))}')
print(f'Files in {monthly_ndvi}: {len(os.listdir(monthly_ndvi))}')
print(f'Files in {monthly_s5p}: {len(os.listdir(monthly_s5p))}')
print(f'Files in {monthly_aerosols}: {len(os.listdir(monthly_aerosols))}')
print(f'Files in {monthly_no2}: {len(os.listdir(monthly_no2))}')
print(f'Files in {monthly_hcho}: {len(os.listdir(monthly_hcho))}')
print(f'Files in {monthly_clouds}: {len(os.listdir(monthly_clouds))}')
print(f'Files in {monthly_population_density}: {len(os.listdir(monthly_population_density))}')
print(f'Files in {grid_path}: {len(os.listdir(grid_path))}')