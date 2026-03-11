# Libraries
import pandas as pd
import numpy as np
import os 
import rasterio as rio
import geopandas as gpd
from sklearn.model_selection import GridSearchCV,GroupKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import root_mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from pykrige import UniversalKriging as UK
from pykrige.rk import Krige
from shapely.geometry import Point
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import KNNImputer
import re
from pathlib import Path
import warnings
from rasterio.enums import Resampling
import matplotlib.pyplot as plt
import shutil
import shap

def count_NAs(band_columns,data_fwame):
    for band_col in band_columns:
        na_count = data_fwame[band_col].isna().sum()
        print(f"Number of NA values in {band_col}: {na_count}")   

def set_timedums(datafwame):
    datafwame['date'] = pd.to_datetime(datafwame['date'])
    month_dummies = pd.get_dummies(datafwame['date'].dt.month, prefix='month')
    datafwame = pd.concat([datafwame, month_dummies], axis=1)
    return datafwame

def drift_funcFt(x, y):
    return np.sin(x) + y**2 - np.exp(-y)

def drift_funcGaus(x, y):
    return x + y + np.random.normal(0, 1) 

# Data Paths for all images
tif_folder = os.path.join(os.path.expanduser('~'), "Documents", "Github", "UCBMasters", "data",'tifs')
folder_paths = ['gridmet', 'ozone10km', 'viirs', 'ccnl', 'ndvi','no2','s5p','population_density','p_grd']
folder_full_paths = [os.path.join(tif_folder, folder_name) for folder_name in folder_paths]
feature_folder_paths = [path for path in folder_full_paths if os.path.isdir(path)]
months_folder_paths = [Path(os.path.join(path, 'monthly')) for path in feature_folder_paths[:-1]]
p_grd_folder_paths = [Path(os.path.join(feature_folder_paths[-1])),Path(os.path.join(months_folder_paths[-1]))]
dates_list = pd.date_range(start='1980-01',end='2023-12',freq='MS').strftime('%Y-%m').tolist()
months_folder_paths
date_pattern = re.compile('|'.join(re.escape(date) for date in dates_list))
matching_file_paths = []
for months_path in months_folder_paths:
    if months_path.is_dir():
        for file_path in months_path.iterdir():
            if file_path.is_file():
                file_name = file_path.name
                if date_pattern.search(file_name):
                    matching_file_paths.append(file_path)
    else:
        print(f"The directory {months_path} does not exist.")

matching_file_paths.append(Path(os.path.join(p_grd_folder_paths[1],'popden_2020-01-01.tif')))
matching_file_paths.append(Path(os.path.join(os.path.expanduser('~'), "Documents", "Github", "UCBMasters", "data",'tifs','elevation','elevation.tif')))
# RF-RK For One Month and Date
# November, 2018
date_str = '2019-03'
images_model_start = [path for path in matching_file_paths if date_str in path.name] + matching_file_paths[-2:]
pred_grid = os.path.join(p_grd_folder_paths[0], f'photuc_grid_{date_str}-01.tif')
output_path = os.path.join(os.path.expanduser('~'), "Documents", "Github", "UCBMasters", "data",'results', 'final_results', 'predicted_grids', 'start',f'photuc_grid_{date_str}-01.tif')
total_bands = 1
band_mapping = [1]
for raster_path in images_model_start:
    with rio.open(raster_path) as src:
        total_bands += src.count
        band_mapping.extend(range(1, src.count + 1))

with rio.open(pred_grid) as base:
    meta = base.meta.copy()
    meta.update(count=total_bands, dtype='float32')     
    with rio.open(output_path, 'w', **meta) as out_raster:
        out_raster.write(base.read(1).astype('float32'), 1)
        current_band = 2
        for raster_path in images_model_start:
            with rio.open(raster_path) as src:
                for band_idx in range(1, src.count + 1):
                    if src.res != base.res or src.shape != base.shape or src.crs != base.crs:
                        data = src.read(band_idx,out_shape=(base.height, base.width),resampling=Resampling.bilinear).astype('float32')
                    else:
                        data = src.read(band_idx).astype('float32')       
                    if data.shape != (base.height, base.width):
                        raise ValueError(f"Resampled data shape {data.shape} does not match target raster shape:\n({base.height}, {base.width}).") 
                    out_raster.write(data, current_band)
                    current_band += 1

print(f"Multi-banded raster saved to {output_path}")

def load_multiband_raster(image_path):
    data_arrays = []
    transforms = []
    image_metadata = None
    with rio.open(image_path) as src:
        for band_idx in range(1, src.count + 1):
            data = src.read(band_idx).astype('float32')
            data_arrays.append(data)
            transforms.append(src.transform)
            if image_metadata is None:
                image_metadata = src.meta.copy()
    return data_arrays, transforms, image_metadata

processed_arrays, transforms, metadata = load_multiband_raster(output_path)
processed_arrays.pop(12)
processed_arrays[10] = np.where(processed_arrays[10] < 0, 0, processed_arrays[10]) #ndvi
processed_arrays[-1] = np.where(processed_arrays[-1] < 0, 0, processed_arrays[-1]) #elevation

def display_raster_bands(raster_data, title="Raster Bands"):
    names = ['Precipitation', 'Specific Humidity', 'Total Downward Solar Radiation','Maximum Temperature', 'Windspeed', 'Burn Index', 'Vapor Pressure Deficit','Toms OZ', "Night Time Lights", 'NDVI','NO2 Total Column Density','O3 Column Number Density','O3 Effective Temperature','Cloud Fraction', 'Population Density: 2020','Elevation']
    n_bands = len(raster_data) 
    rows, cols = 4,4
    fig, axes = plt.subplots(rows, cols, figsize=(11,8.5))
    axes = axes.flatten()
    for i, ax in enumerate(axes):
        if i < n_bands:
            band = raster_data[i]
            band = np.where(band == 0, np.nan, band)
            valid_values = band[~np.isnan(band)]
            band_min = valid_values.min() if valid_values.size > 0 else float('nan')
            band_max = valid_values.max() if valid_values.size > 0 else float('nan')
            band_mean = valid_values.mean() if valid_values.size > 0 else float('nan')
            im = ax.imshow(band, cmap='viridis')
            ax.set_title(f"{names[i] if i < len(names) else f'Band {i + 1}'}", fontsize=10)
            ax.set_xlabel(f"Mean: {band_mean:.4f}\nMin: {band_min:.4f}, Max: {band_max:.4f}", fontsize=8)
            fig.colorbar(im, ax=ax, orientation="vertical", shrink=0.75)
        else:
            ax.axis('off')
    fig.suptitle(title, fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()

display_raster_bands(processed_arrays[1:], title="Raster Data for March, 2019")

# count_NAs(pred_features.columns, pred_features)
# Point Model Training/Testing
oz_since_2018_df = pd.read_csv(os.path.join('~','Documents','Github','UCBMasters','data','results','final_results',"ozone_2018_2023_dataset.csv"), index_col=0)
filtered_df = oz_since_2018_df[oz_since_2018_df['avg_monthly_val'].notna()]
missing_counts = oz_since_2018_df.groupby(['site_id'])['avg_monthly_val'].apply(lambda x: x.isna().sum())
full_monitors = missing_counts[missing_counts == 0].index
partial_monitors = missing_counts[(missing_counts >= 1) & (missing_counts < 20)].index

final_monitor_selection = oz_since_2018_df.drop(columns=['precip','temp_max', 'bnid','spf_hmdty', 'vprps_def', 'ozone','absorbing_aerosol_index','stratospheric_NO2_column_number_density','tropospheric_HCHO_column_number_density', 'cloud_index', 'O3_effective_temperature','cloud_fraction','pop_den', 'dist2rds']).copy()
imputated_monitor_36 =final_monitor_selection[(final_monitor_selection['site_id'].isin(full_monitors)) | (final_monitor_selection['site_id'].isin(partial_monitors))]
imputated_monitor_36 = imputated_monitor_36.sort_values(by='date').reset_index(drop=True)
knn_features = imputated_monitor_36.drop(columns=['site_id', 'date', 'datum','geometry']).columns
imputer = KNNImputer(n_neighbors=12)
# Imputation Error
full_monitors = missing_counts[missing_counts == 0].index
partial_monitors = missing_counts[(missing_counts >= 1) & (missing_counts < 20)].index
imputated_error =final_monitor_selection[(final_monitor_selection['site_id'].isin(full_monitors)) | (final_monitor_selection['site_id'].isin(partial_monitors))]
imputated_error = imputated_error.sort_values(by='date').reset_index(drop=True)
imputated_error = imputated_error[imputated_error['avg_monthly_val'].notna()]
imp_compar = imputated_error[['site_id','date','avg_monthly_val']].copy()
fraction_to_nan = 0.1
imputated_error['avg_monthly_val'] = imputated_error['avg_monthly_val'].mask(np.random.rand(len(imputated_error)) < fraction_to_nan)
knn_features = imputated_error.drop(columns=['site_id', 'date', 'datum','geometry']).columns
imputer = KNNImputer(n_neighbors=12) 
imputated_error[knn_features] = imputer.fit_transform(imputated_error[knn_features])
print(f'KNN Imputation Error: {round(np.mean(abs(imp_compar['avg_monthly_val'] - imputated_error['avg_monthly_val'])/imp_compar['avg_monthly_val']*100),3)}')

# Model Data
imputated_monitor_36[knn_features] = imputer.fit_transform(imputated_monitor_36[knn_features])

# Model Params
rf_params = {'bootstrap':[True, False],'max_features':['sqrt','log2'],'criterion':['squared_error','absolute_error', 'neg_mean_squared_error'],'n_estimators':np.arange(100,300,10)}
rk_params = {'variogram_model':["linear",'power','gaussian','spherical','exponential','hole-effect'],'drift_terms': ['function'], 'nlags':[12,13,14,15,20], 'functional_drift':[[drift_funcGaus],[drift_funcFt]]}

# def rf_rk(test_dataframe_version, rf_params, rk_params, date='2019-03'):
date_str = '2019-03'
test_dataframe_version = imputated_monitor_36[imputated_monitor_36.date==date_str].copy()
x_pre_trns = test_dataframe_version.drop(columns=['lat','long','geometry','datum']).copy()
ids = test_dataframe_version.site_id.reset_index(drop=True)

k_split = round(len(np.unique(ids))/6) 
group_kfold = GroupKFold(n_splits=k_split)
X_mons = x_pre_trns.drop(columns=['site_id','date','avg_monthly_val']).reset_index(drop=True)
X_mons.columns = ['elevation','down_srad','temp_ax','wdsp','ndvi','nighttime_lights','NO2_tco','O3_tco']
y_pred = x_pre_trns['avg_monthly_val'].reset_index(drop=True)
group_kfold=GroupKFold(n_splits=k_split)
scv = GridSearchCV(RandomForestRegressor(random_state=42), param_grid=rf_params, cv=group_kfold.split(X_mons, y_pred, ids), scoring='neg_mean_squared_error', n_jobs=-1)
scv_best = scv.fit(X_mons,np.ravel(y_pred))
krige_info =  pd.DataFrame({'site_id':ids,'lat':test_dataframe_version.lat,'long':test_dataframe_version.long,'datum':test_dataframe_version.datum})
model_info = {'site_id':[],'act':[],'pred':[]}
for train, test in group_kfold.split(X_mons, y_pred, ids):
    x_tr, x_te = X_mons.iloc[train,],X_mons.iloc[test,]
    y_tr, y_te = y_pred[train],y_pred[test]
    sites_tr, sites_te = ids[train], ids[test]
    rf = RandomForestRegressor(**scv_best.best_params_)
    rf.fit(x_tr,y_tr)
    model_info['act'].extend(y_te)
    model_info['site_id'].extend(sites_te)
    model_info['pred'].extend(rf.predict(x_te))

join_dis = pd.DataFrame(model_info)
krige_df = pd.merge(krige_info, join_dis, how="left", on=['site_id'])
explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_mons)
shap.summary_plot(shap_values, X_mons, plot_type="bar")
shap.summary_plot(shap_values, X_mons)

output_path = os.path.join(os.path.expanduser('~'), "Documents", "Github", "UCBMasters", "data",'results', 'final_results', 'predicted_grids', 'start',f'photuc_grid_{date_str}-01.tif')
fin_file = os.path.join(os.path.expanduser('~'), "Documents", "Github", "UCBMasters", "data",'results', 'final_results', 'predicted_grids', 'fin',f'photuc_grid_{date_str}-01.tif')
shutil.copy(output_path, fin_file)
['down_srad', 'wdsp', 'ndvi','nighttime_lights', 'NO2_tco']
flat_data = { 
    'elevation': processed_arrays[16].flatten(),
    'down_srad': processed_arrays[3].flatten(),
    'temp_ax': processed_arrays[4].flatten(),
    'wdsp': processed_arrays[5].flatten(),
    'ndvi': processed_arrays[10].flatten(),
    'nighttime_lights': processed_arrays[9].flatten(),
    'NO2_tco': processed_arrays[11].flatten(),
    'O3_tco': processed_arrays[12].flatten(),
}

pred_features = pd.DataFrame(flat_data)

with rio.open(fin_file) as src:
    raster_data = src.read(1)
    raster_meta = src.meta

predicted_values = scv_best.predict(pred_features)
predicted_raster = predicted_values.reshape(raster_data.shape)

with rio.open(fin_file,'w',**raster_meta) as dst:
    dst.write(predicted_raster, 1)

with rio.open(fin_file, 'r') as src:
    raster_data = src.read(1)
    plt.figure(figsize=(10, 8))
    plt.imshow(raster_data, cmap='viridis')
    plt.colorbar(label='Pixel Values')
    plt.title(f'Raster Data: {fin_file}')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.show()

krige_df['resid']=krige_df['act'].values-krige_df['pred']
proj_fix_nad83=krige_df[krige_df.datum=='NAD83']
proj_fix_wgs84=krige_df[krige_df.datum=='WGS84']
wgs84=gpd.GeoDataFrame(proj_fix_wgs84,geometry=[Point(lon,lat) for lon,lat in zip(proj_fix_wgs84['long'],proj_fix_wgs84['lat'])],crs='EPSG:4326').set_crs(epsg=4326)
nad83=gpd.GeoDataFrame(proj_fix_nad83,geometry=[Point(lon,lat) for lon,lat in zip(proj_fix_nad83['long'],proj_fix_nad83['lat'])],crs='EPSG:4269').set_crs(epsg=4269)
nad83_to_wgs84 = nad83.to_crs(wgs84.crs)
x_pre_trns=pd.concat([wgs84,nad83_to_wgs84])
dated_krige = x_pre_trns[x_pre_trns.date==date_str]
estimator = GridSearchCV(Krige(method= "universal", coordinates_type= "geographic", verbose=True), cv=group_kfold.split(x_pre_trns.geometry, x_pre_trns['resid'], x_pre_trns.site_id), param_grid=rk_params)

estimator.fit(X=np.array(list(zip(x_pre_trns.geometry.x,x_pre_trns.geometry.y))), y=x_pre_trns['resid'].values, groups=group_kfold.split(x_pre_trns.geometry, x_pre_trns['resid'], x_pre_trns.site_id))

UK_mons = UK(train_dat.geometry.x, train_dat.geometry.y, y_train.values,**estimator.best_params_, verbose=True)
z1, ss1 = UK_mons.execute('grid', test_dat.geometry.x, test_dat.geometry.y) 

sc_back = pd.DataFrame(sc.inverse_transform(test_dat[['act_val','rf_predicted', 'resid']]), columns=['act_val','rf_predicted', 'resid'])
test_dat = test_dat.reset_index(drop=True)
test_dat['rf_predicted']=sc_back['rf_predicted']
test_dat['act_val']=sc_back['act_val']
test_dat['resid']=sc_back['resid']
smarkt_val = test_dat['rf_predicted']+test_dat['resid']

UK_fin = UK(lons, lats, zdata,**est_test.best_params_, verbose=True)
z1, ss1 = UK_fin.execute('grid', lons, lats)
xmin, ymin, xmax, ymax = photuc.total_bounds
xmin = xmin-1
xmax = xmax+1

ymin = ymin-1
ymax = ymax+1

grid_lon = np.linspace(xmin, xmax, 100)
grid_lat = np.linspace(ymin, ymax, 100)

z1, ss1 = UK.execute('grid', grid_lon, grid_lat)

xintrp, yintrp = np.meshgrid(grid_lon, grid_lat) 