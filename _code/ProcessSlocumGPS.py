# Code for processing slocum GPS data
# Inputs - dcd files (dbdreader functions decompress dcd files but you need to point to the cache files)
# Outputs - one csv file with surface GPS data (measured) and one csv file with dead reckoned locations (calculated) with depth, matching NGDAC formats

# %% Import modules
import dbdreader
import numpy as np
from datetime import datetime, timezone
import csv

# %% Create Functions
## function to extract gps points from dcd files
def extract_gps_from_dbd(file_path, cache_path=None): 
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
dbd_files = r'C:\Users\kourtney.burger\Desktop\Test_dbd_data\*.dcd' 
output_csv = r'C:\Users\kourtney.burger\Desktop\Test_dbd_data\gps_data.csv'

# run functions
gps_data = extract_gps_from_dbd(dbd_files, cache_files)
export_to_csv(gps_data, output_csv)

# # %% quick data check
# import pandas as pd
# import plotly.express as px

# df = pd.DataFrame(gps_data)

# fig = px.scatter_mapbox(df, lat="lat", lon="lon", hover_data=["timestamp"], zoom=9)

# fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
# fig.show()