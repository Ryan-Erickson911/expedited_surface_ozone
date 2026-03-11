import pandas as pd
import requests
import os
import geopandas as gpd
import geemap
import ee
import rasterio as ro
from datetime import datetime, timedelta
from shapely.geometry import Point
########### VARS #############

__name__ = "__main__"

if not ee.Authenticate(auth_mode=os.environ.get('host_key')):
    ee.Authenticate(auth_mode=os.environ.get('host_key'),force=True)
    
epa_email = os.environ.get('epa_email') # you will need your own EPA account
epa_key = os.environ.get('epa_key')

#################################################################
#Monitor related 
# - counts missing monitors in dataset
def count_NAs(band_columns,data_fwame):
    for band_col in band_columns:
        na_count = data_fwame[band_col].isna().sum()
        print(f"Number of NA values in {band_col}: {na_count}")  
# - takes json formatted data and exports a data frame
def json_to_df(json_data):
    return pd.DataFrame(json_data["Data"])
#creates http server address and exports a list of strings to loop through. USed in monthly data creation
def get_epa_data(param, state_code, bdate, edate, email=epa_email, key=epa_key):
    url=f"https://aqs.epa.gov/data/api/dailyData/byState?email={email}&key={key}&param={param}&bdate={bdate}&edate={edate}&state={state_code}"
    try:
        response=requests.get(url)
        response.raise_for_status()
        monitors_data=response.json()
        return json_to_df(monitors_data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()
# converts monitors to spatial object for use in python

# def epa_data_help():
#     return 'https://docs.airnowapi.org/account/request/'


# def mon_to_gdf(monitor_df):
#     proj_fix_nad83=monitor_df[monitor_df.datum=='NAD83']
#     proj_fix_wgs84=monitor_df[monitor_df.datum=='WGS84']
#     wgs84=gpd.GeoDataFrame(proj_fix_wgs84,geometry=[Point(lon,lat) for lon,lat in zip(proj_fix_wgs84['long'],proj_fix_wgs84['lat'])],crs='EPSG:4326').set_crs(epsg=4326)
#     nad83=gpd.GeoDataFrame(proj_fix_nad83,geometry=[Point(lon,lat) for lon,lat in zip(proj_fix_nad83['long'],proj_fix_nad83['lat'])],crs='EPSG:4269').set_crs(epsg=4269)
#     nad83_to_wgs84 = nad83.to_crs(wgs84.crs)
#     gdf=pd.concat([wgs84,nad83_to_wgs84])
#     gdf.crs
#     return gdf



# # Main function for final monthly monitor data. Gathers data from http server on EPA website. An account must be created and verified by the EPA to gain access. 
# # for testing => year_start, year_end, param_code,state_res,county_res=2018,2024,"44201","04",["Maricopa", "Pinal", "Pima"] -> units_of_measure = PPM
# def get_daily_epa_data(year_start=2018, year_end=2024, param_code="44201",state_res="04", county_res=["Maricopa", "Pinal", "Pima"]):
#     years_list=range(year_start, year_end + 1) #list of years
#     param=param_code #aerosol param code from EPA
#     state=state_res #state code (string)
#     photuc_metro_counties=county_res #county names (list)
#     all_data=[]
#     quick_summary=[]
#     for year in years_list:
#         print(f'\nDownloading {year} monitor data from EPA')
#         download=get_epa_data(email=epa_email, key=epa_key, param=param, state_code=state, year=str(year))
#         if download.empty:
#             print(f"No monitor data avlaiable for {year}")
#             continue
#         print(f'Adding {year} monthly averages to dataset')
#         filtered_oz=download[download["county"].isin(photuc_metro_counties)].copy()
#         filtered_oz.loc[:, 'site_id'] = filtered_oz.loc[:,['state_code', 'county_code', 'site_number']].astype(str).agg(''.join, axis=1)
#         ozstand_filter = filtered_oz.loc[(filtered_oz['pollutant_standard'] == 'Ozone 8-hour 2015')]
#         site_ids=ozstand_filter['site_id'].unique().copy()
#         print(f'Number of sites found in {year}: {len(site_ids)}')
#         mtr_yr_ct_daily_avg_stat_plot_1=[year,len(site_ids)]
#         all_days_in_range=pd.date_range(start=f'{year}-01-01', end=f'{year}-12-31', freq="D").strftime('%Y-%m-%d').tolist()
#         all_sites_and_days = pd.DataFrame(([site_id,date] for site_id in site_ids for date in all_days_in_range), columns=['site_id','date_local'])
#         final=all_sites_and_days.merge(ozstand_filter, on=['site_id','date_local'], how='left')
#         fill_columns = ['latitude', 'longitude', 'site_id', 'datum','date_local','local_site_name']  
#         filled_df = final.groupby('site_id')[fill_columns].ffill().bfill()
#         final_updated = final.copy()
#         final_updated[fill_columns] = filled_df
#         final=final_updated[['latitude', 'longitude', 'site_id', 'datum','first_max_value','date_local','aqi','local_site_name']]
#         all_data.append(final)
#         quick_summary.append(mtr_yr_ct_daily_avg_stat_plot_1)
#     final_df=pd.concat(all_data, ignore_index=True)
#     final_sum = pd.DataFrame(quick_summary, columns=['year','num_sites'])
#     monitors=final_df[['latitude', 'longitude', 'site_id', 'datum','first_max_value','date_local','aqi','local_site_name']]
#     monitors.columns=['lat', 'long','site_id', 'datum', 'max_value', 'date','aqi','site_name']
#     print(f'Monitors over Time:\n{final_sum}')
#     print(f'Number of unique monitors: {monitors["lat"].nunique()}')
#     print('Complete')
#     return monitors

# # This script gathers the necessary raster data from Google Earth Engine (GEE). This will be used in the extraction and model output process.
# # A function to produce a list of daily date ranges in the format necessary for http communication. 
# def get_daily_intervals(start_date, end_date):
#     start = datetime.strptime(start_date, '%Y-%m-%d')
#     end = datetime.strptime(end_date, '%Y-%m-%d')
#     intervals = []
#     current = start
#     while current < end:
#         next_day = current + timedelta(days=1)
#         intervals.append((current.strftime('%Y-%m-%d'), next_day.strftime('%Y-%m-%d')))
#         current = next_day
#     return intervals
# # Raster Imputation
# def get_raster_differences(nf_name,folder='path', can_be_zero=True):
#     files = os.listdir(folder)
#     if not can_be_zero:
#         for raster in files:
#             check = os.path.join(folder, raster)
#             with ro.open(check) as src:
#                 vals = src.read() 
#                 if 0 in vals:
#                     delete=True
#                 else:
#                     delete=False
#             if delete:
#                 os.remove(check)
#                 print(f'Removed {check} for having 0 output over known value')
#         files = os.listdir(folder)
#     else:
#         files = os.listdir(folder)
#     files_sorted = sorted(files,key=lambda x: datetime.strptime(x[-14:-4], "%Y-%m-%d"))
#     paths_sorted = [os.path.join(folder, f) for f in files_sorted]
#     dates = [(paths_sorted[i], paths_sorted[i+1]) for i in range(len(paths_sorted) - 1)]
#     for x,y in dates:
#         s_path = os.path.join(folder,x)
#         e_path = os.path.join(folder,y)
#         if x[:-14]!=y[:-14]:
#             continue
#         else:
#             start=str(x[-14:-4])
#             end=str(y[-14:-4])
#             date1=datetime.strptime(start, "%Y-%m-%d")
#             date2=datetime.strptime(end, "%Y-%m-%d")
#             difference=int((date2-date1).days) 
#         if difference >= 2:        
#             with ro.open(s_path) as src_start, ro.open(e_path) as src_end:
#                 data_1 = src_start.read() 
#                 data_2 = src_end.read()  
#                 profile = src_start.profile
#             daily_change = (data_2 - data_1) / difference
#             current_data = data_1.copy()
#             for day in range(1, difference):
#                 date_str = (date1 + timedelta(days=day)).strftime("%Y-%m-%d")# Create filename
#                 output_filename = os.path.join(folder, f"{nf_name}_{date_str}.tif")
#                 current_data = (current_data+daily_change)
#                 with ro.open(output_filename, "w", **profile) as dst:
#                     dst.write(current_data)
#             print(f"Finished generating daily interpolated TIFFs {nf_name}: {start} to {end}.")

# def get_imagery(file_path=str, file_prefix= 'gmet', first_day="2018-12-01" , last_day="2025-01-31", collection='IDAHO_EPSCOR/GRIDMET', bands=['pr', 'sph', 'srad','tmmn', 'tmmx', 'vs', 'bi', 'vpd'], band_names=['precip', 'spf_hmdty', 'down_srad', 'min_surf_temp','max_surf_temp', 'wdsp', 'bnid', 'vprps_def'],resampling_method='nearest',mask_val=None,resolution=500):
#     intervals = get_daily_intervals(first_day,last_day)
#     if not os.path.exists(file_path):
#         os.makedirs(file_path)
#         n_files=0
#         print(f"Created Daily {file_prefix} Collection folder")
#     else:
#         n_files=len(os.listdir(file_path))
#     print(f"{file_prefix.title()} Imagery:")
#     if n_files<1:
#         for start, end in intervals:
#             out_path = os.path.join(file_path,f'{file_prefix}_{start}.tif')
#             if file_prefix in ['gmet']:
#                 main_gm_col = ee.ImageCollection(collection).select(bands,band_names).filterDate(start, end).first()
#             else:
#                 main_gm_col = ee.ImageCollection(collection).select(bands,band_names).filterDate(start, end).mean()
#             if main_gm_col.bandNames().size().getInfo() > 0:
#                 if resampling_method=='nearest':
#                     geemap.ee_export_image(main_gm_col,out_path,region=photuc.geometry(),crs='EPSG:4326', scale=resolution, unmask_value=mask_val)
#                 else:
#                     resampled = main_gm_col.resample(resampling_method) #['bilinear', 'bicubic']
#                     geemap.ee_export_image(resampled,out_path,region=photuc.geometry(),crs='EPSG:4326', scale=resolution, unmask_value=mask_val)
#             else:
#                 continue
#     elif len(os.listdir(file_path))>2280:
#         print(f"   Likely has full coverage: N = {len(os.listdir(file_path))}")
#     else:
#         print(f"    {len(os.listdir(file_path))} files in {file_path}\n    Completing File Download...")
#         names = os.listdir(file_path)
#         fd_dts = [x[-14:-4] for x in names]
#         for start, end in intervals:
#             out_path = os.path.join(file_path,f'{file_prefix}_{start}.tif')
#             if start not in fd_dts:
#                 if file_prefix in ['gmet']:
#                     main_gm_col = ee.ImageCollection(collection).select(bands,band_names).filterDate(start, end).first()
#                 else:
#                     main_gm_col = ee.ImageCollection(collection).select(bands,band_names).filterDate(start, end).mean()  # type: ignore
#             else:
#                 continue
#             if main_gm_col.bandNames().size().getInfo() > 0:
#                 if resampling_method=='nearest':
#                     geemap.ee_export_image(main_gm_col,out_path,region=state.geometry(),crs='EPSG:4326', scale=resolution, unmask_value=mask_val)
#                 else:
#                     resampled = main_gm_col.resample(resampling_method) #['bilinear', 'bicubic']
#                     geemap.ee_export_image(resampled,out_path,region=state.geometry(),crs='EPSG:4326', scale=resolution, unmask_value=mask_val)
#             else:
#                 continue
#         print(f"   path = {file_path}\n   N = {len(os.listdir(file_path))}\nmoving on...\n")

# # get boundary - must know FIPS - update for list of county FIPS
# def get_aoi(st_abbv=str, folder='data', obj=False):
#     ee.Initialize()
#     '''
    
#     Accesses Google Earth Engine (GEE) to download the AOI of a given state into a specified folder.
#     Requires proper API setup, path to data folder, and state. The state should be abrreviated (i.e., AZ, CA, IA, OH, WA, etc.).
    
#     Returns an ee.FeatureCollection. If obj=True, returns path to downloaded shapefile.'''
#     look = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
#     while True:
#         try:
#             file_path=os.path.join(os.getcwd(),folder,'aoi')
#             os.makedirs(file_path, exist_ok=True)
#         except TypeError:
#             folder = input("Please check folder name to save the AOI: ")
#             continue

#         if st_abbv in look:
#             break
#         else:
#             st_abbv = input("State not found, please check the abbreviation: ")
#             continue
#     print("Creating AOI...")
#     dataset = ee.FeatureCollection('TIGER/2020/BG').filter(ee.Filter.eq('STATEFP', st_abbv))
#     arizonaUnion = dataset.union()
#     roi = arizonaUnion.geometry() 
#     state = ee.FeatureCollection(roi)
#     if obj:
#         fpath = os.path.join(file_path,f'{st_abbv}_aoi.shp')
#         print(f'Saving EE object: {fpath}') 
#         geemap.ee_export_vector(state, fpath, verbose=True)
#         return fpath
#     else:
#         return state

if __name__ == "__main__":
    this = get_epa_data("44201","04", "20200101", "20200102", epa_email, epa_key)
    print(epa_email)
    print(this.head)