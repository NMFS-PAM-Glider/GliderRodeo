# Code for processing SeaExplorer glider GPS data
# Inputs - Alseamar SeaExplorer .gz files (specifically the .gli platform files)
# Outputs - one csv file with surface GPS data and one csv file with dead reckoned locations

# %% Import modules
import pandas as pd
import glob
from datetime import datetime, timezone
import csv
# import plotly.express as px
import numpy as np

# %% Create Functions
def nmea_to_decimal(nmea_val):
    """
    Converts NMEA format (DDMM.MMMM or DDDMM.MMMM) to Decimal Degrees.
    Handles negative values (South/West) appropriately.
    """
    if pd.isna(nmea_val) or nmea_val == 0:
        return np.nan
    
    try:
        val = float(nmea_val)
    except ValueError:
        return np.nan
        
    sign = -1 if val < 0 else 1
    val = abs(val)
    
    # Extract degrees (the hundreds/thousands place) and minutes (the rest)
    degrees = int(val / 100)
    minutes = val - (degrees * 100)
    
    decimal_degrees = sign * (degrees + (minutes / 60.0))
    return decimal_degrees

def process_seaexplorer_files(file_pattern):
    """
    Reads and concatenates SeaExplorer .gz navigation files.
    """
    files = glob.glob(file_pattern)
    if not files:
        print("No files found matching the pattern.")
        return pd.DataFrame()
    
    df_list = []
    for file in files:
        # pandas reads gzip compressed, semicolon-separated files directly
        df = pd.read_csv(file, sep=';', compression='gzip', on_bad_lines='skip') 
        df_list.append(df)
        
    merged_df = pd.concat(df_list, ignore_index=True)
    merged_df.columns = merged_df.columns.str.strip()
    
    # Sort by time and format
    if 'Timestamp' in merged_df.columns:
        merged_df['timestamp_dt'] = pd.to_datetime(merged_df['Timestamp'], dayfirst=True, errors='coerce', utc=True)
        merged_df.sort_values('timestamp_dt', inplace=True)
        merged_df['timestamp'] = merged_df['timestamp_dt'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
    # Convert NMEA coordinates to Decimal Degrees
    if 'Lat' in merged_df.columns and 'Lon' in merged_df.columns:
        merged_df['Lat'] = merged_df['Lat'].apply(nmea_to_decimal)
        merged_df['Lon'] = merged_df['Lon'].apply(nmea_to_decimal)
    
    return merged_df

def extract_surface_gps(df, depth_threshold=1.0):
    df_valid = df.dropna(subset=['Lat', 'Lon']).copy()
    df_surface = df_valid[df_valid['Depth'] < depth_threshold]
    
    extracted_points = []
    for _, row in df_surface.iterrows():
        extracted_points.append({
            'timestamp': row['timestamp'],
            'lat': row['Lat'],
            'lon': row['Lon']
        })
    return extracted_points

def extract_drloc_and_depth(df, depth_threshold=1.0):
    df_valid = df.dropna(subset=['Lat', 'Lon', 'Depth']).copy()
    df_underwater = df_valid[df_valid['Depth'] >= depth_threshold]
    
    extracted_points = []
    for _, row in df_underwater.iterrows():
        extracted_points.append({
            'timestamp': row['timestamp'],
            'lat': row['Lat'],
            'lon': row['Lon'],
            'depth_m': row['Depth']
        })
    return extracted_points

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
# Set up directories 
seaexplorer_files = r'E:\alseamar\_KB files\dataFromAlseamarDrive\SEA117M026_rodeofiles\rodeo\*.gli.sub.*.gz'

# Run functions
print("Loading SeaExplorer data and converting coordinates...")
df_all = process_seaexplorer_files(seaexplorer_files)

if not df_all.empty:
    gps_data = extract_surface_gps(df_all, depth_threshold=1.0)
    export_to_csv(gps_data, r'C:\Users\kourtney.burger\Documents\GitHub\GliderRodeo\data\gps\seaexplorer_GPS_Surface.csv')
    
    drloc_depth_data = extract_drloc_and_depth(df_all, depth_threshold=1.0)
    export_to_csv(drloc_depth_data, r'C:\Users\kourtney.burger\Documents\GitHub\GliderRodeo\data\gps\seaexplorer_GPS_DeadReckoned.csv')
    
    # %% Plot Surface GPS (Updated for Maplibre)
    print("Plotting Surface GPS...")
    df_gps = pd.DataFrame(gps_data)
    if not df_gps.empty:
        fig_gps = px.scatter_map(df_gps, lat="lat", lon="lon", hover_data=["timestamp"], zoom=9)
        fig_gps.update_layout(map_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
        fig_gps.show()
    
    # %% Plot Underwater Track (Updated for Maplibre)
    print("Plotting Underwater Track...")
    df_underwater = pd.DataFrame(drloc_depth_data)
    if not df_underwater.empty:
        fig_dr = px.scatter_map(
            df_underwater, 
            lat="lat", 
            lon="lon", 
            color="depth_m",                     
            color_continuous_scale="blues",      
            hover_data=["timestamp", "depth_m"], 
            zoom=9,
            title="Underwater Glider Track (Color = Depth in meters)"
        )
        fig_dr.update_layout(map_style="open-street-map", margin={"r":0,"t":40,"l":0,"b":0})
        fig_dr.show()
else:
    print("No data processed. Please check your file path or the .gz files.")