# Code for processing slocum GPS data
# Inputs - dcd files (dbdreader functions decompress dcd files but you need to point to the cache files)
# Outputs - one csv file with surface GPS data (measured) and one csv file with dead reckoned locations (calculated) with depth, matching NGDAC formats

# %% Import modules
import dbdreader
import numpy as np
from datetime import datetime, timezone
import csv

# %% Create Functions
## function to extract surface gps points from dcd files
def extract_surfac_gps_from_dbd(file_path, cache_path=None): 
    dbd = dbdreader.MultiDBD(pattern=file_path, cacheDir=cache_path)

    time_lat, lat_raw = dbd.get('m_gps_lat')
    time_lon, lon_raw = dbd.get('m_gps_lon')

    valid_indices = ~np.isnan(lat_raw)
    valid_times = time_lat[valid_indices]
    valid_lats = lat_raw[valid_indices]
    valid_lons = lon_raw[valid_indices]

    extracted_points = []

    for t, lat, lon in zip(valid_times, valid_lats, valid_lons):
        dt_object = datetime.fromtimestamp(t, tz=timezone.utc)
        timestamp = dt_object.strftime('%Y-%m-%dT%H:%M:%SZ')

        lat_out = -999.0 if np.isnan(lat) else lat
        lon_out = -999.0 if np.isnan(lon) else lon
        
        extracted_points.append({
            'timestamp': timestamp,
            'lat': lat_out,
            'lon': lon_out
        })

    return extracted_points

## function to extract dead reckoned locations and depth from dcd files
def extract_drloc_and_depth_from_dbd(file_path, cache_path=None): 
    dbd = dbdreader.MultiDBD(pattern=file_path, cacheDir=cache_path)

    time_lat, lat_raw = dbd.get('m_lat')
    time_lon, lon_raw = dbd.get('m_lon')

    time_depth, depth_raw = dbd.get('m_depth')

    valid_indices = ~np.isnan(lat_raw)
    valid_times = time_lat[valid_indices]
    valid_lats = lat_raw[valid_indices]
    valid_lons = lon_raw[valid_indices]

    valid_depth_idx = ~np.isnan(depth_raw)
    clean_time_depth = time_depth[valid_depth_idx]
    clean_depth = depth_raw[valid_depth_idx]

    interpolated_depths = np.interp(valid_times, clean_time_depth, clean_depth)

    extracted_points = []

    for t, lat, lon, depth in zip(valid_times, valid_lats, valid_lons, interpolated_depths):
        dt_object = datetime.fromtimestamp(t, tz=timezone.utc)
        timestamp = dt_object.strftime('%Y-%m-%dT%H:%M:%SZ')

        lat_out = -999.0 if np.isnan(lat) else lat
        lon_out = -999.0 if np.isnan(lon) else lon
        depth_out = -999.0 if np.isnan(depth) else depth
        
        extracted_points.append({
            'timestamp': timestamp,
            'lat': lat_out,
            'lon': lon_out,
            'depth_m': depth_out
        })

    return extracted_points

## function to save gps as csv
def export_to_csv(data, output_filename):
    if not data:
        print("No data found to export.")
        return
        
    headers = data[0].keys()
    with open(output_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

# %% EXAMPLE
# set up directories
cache_files = r'C:\Users\kourtney.burger\Documents\GitHub\standard-glider-files\Cache'
dbd_files = r'C:\Users\kourtney.burger\Desktop\Test_dbd_data\unit_1024-20260309\*.dcd'

# run functions
gps_data = extract_surfac_gps_from_dbd(dbd_files, cache_files)
export_to_csv(gps_data, r'C:\Users\kourtney.burger\Desktop\Test_dbd_data\unit_1024-20260309/DeploymentID_GPS_Surface.csv')

drloc_depth_data = extract_drloc_and_depth_from_dbd(dbd_files, cache_files)
export_to_csv(drloc_depth_data, r'C:\Users\kourtney.burger\Desktop\Test_dbd_data\unit_1024-20260309/DeploymentID_GPS_DeadReckoned.csv')


# %% quick data check for surface gps
import pandas as pd
import plotly.express as px

df = pd.DataFrame(gps_data)

fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_data=["timestamp"], zoom=9)

fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

# %% quick data check for dead reckoned
df_underwater = pd.DataFrame(drloc_depth_data)

df_clean = df_underwater[(df_underwater['depth_m'] != -999.0) & (df_underwater['lat'] != -999.0)]

fig = px.scatter_mapbox(
    df_clean, 
    lat="lat", 
    lon="lon", 
    color="depth_m",                     
    color_continuous_scale="blues",      
    hover_data=["timestamp", "depth_m"], 
    zoom=9,
    title="Underwater Glider Track (Color = Depth in meters)"
)

fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":40,"l":0,"b":0})
fig.show()