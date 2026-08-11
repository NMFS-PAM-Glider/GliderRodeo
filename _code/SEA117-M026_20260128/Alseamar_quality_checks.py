# quality checks 
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import os
import polars as pl

# %% check for start and end timestamps 
nc_file = r"C:\Users\kourtney.burger\Documents\GitHub\GliderRodeo\data\seaexplorer\L0-timeseries\SEA117.26.nc"

with xr.open_dataset(nc_file) as ds:
    print("--- FINAL NETCDF TIMELINE ---")
    print("Starts:", ds['time'].min().values)
    print("Ends:  ", ds['time'].max().values)
    print("Total Rows:", len(ds['time']))

# %% check for data gaps
# Load your processed timeseries
nc_file = r"C:\Users\kourtney.burger\Documents\GitHub\GliderRodeo\data\seaexplorer\L0-timeseries\SEA117.26.nc"

with xr.open_dataset(nc_file) as ds:
    # Convert to a pandas dataframe for easy plotting
    df = ds[['temperature', 'conductivity', 'pressure', 'salinity']].to_dataframe()

plt.figure(figsize=(12, 6))
# This creates a "matrix" plot where data is colored, and missing data (NaN) is white
plt.imshow(df.T.isna(), aspect='auto', cmap='binary_r', interpolation='none')

plt.yticks(range(len(df.columns)), df.columns)
plt.title("Data Availability Matrix (Black = Data Present, White = Missing/Gaps)")
plt.xlabel("Data Points (Chronological)")
plt.tight_layout()
plt.show()


# %% Check native sensor resolutions and max gaps in the final NetCDF
import xarray as xr
import pandas as pd
import numpy as np

nc_file = r"C:\Users\kourtney.burger\Documents\GitHub\GliderRodeo\data\seaexplorer\L0-timeseries\SEA117.26.nc"

with xr.open_dataset(nc_file) as ds:
    # 1. Master CTD Data Frequency (Master Timebase)
    master_times = pd.Series(ds['time'].values)
    ctd_deltas = master_times.diff().dt.total_seconds()
    
    # 2. Native Flight Log Frequency (Pitch, Roll, Heading)
    flight_times = pd.Series(ds['time'].where(~np.isnan(ds['pitch']), drop=True).values)
    flight_deltas = flight_times.diff().dt.total_seconds()

print("==================================================")
print("          SENSOR RESOLUTION PROFILE               ")
print("==================================================")

# Analyze CTD (Legato Payload)
print(f"--- Legato CTD (Science Payload) ---")
print(f"Most common sampling rate (Mode): {ctd_deltas.mode()[0]:.1f} seconds")
print(f"Average sampling rate (Mean):     {ctd_deltas.mean():.1f} seconds")
print(f"Highest resolution captured:       {ctd_deltas.min():.1f} seconds")
print(f"Lowest resolution (Longest gap):  {ctd_deltas.max() / 60.0:.1f} minutes\n")

# Analyze Flight Navigation (Flight Computer)
print(f"--- Flight Computer (Pitch, Roll, Heading) ---")
if len(flight_times) > 1:
    print(f"Most common sampling rate (Mode): {flight_deltas.mode()[0]:.1f} seconds")
    print(f"Average sampling rate (Mean):     {flight_deltas.mean():.1f} seconds")
    print(f"Highest resolution captured:       {flight_deltas.min():.1f} seconds")
    print(f"Lowest resolution (Longest gap):  {flight_deltas.max() / 60.0:.1f} minutes\n")
else:
    print("Could not calculate flight log resolution (insufficient data).\n")

# 3. Surface Transmission Summary
print(f"--- Surface Telemetry / Satellite Gaps ---")
surface_gaps = ctd_deltas[ctd_deltas > 60.0]
print(f"Total satellite/surface intervals detected: {len(surface_gaps)}")
if len(surface_gaps) > 0:
    print(f"Average surface interval duration:        {surface_gaps.mean() / 60.0:.1f} minutes")
print("\n--- Longest Track Gap Isolation ---")

# Dynamically extract the specific timestamps for the longest gap
max_gap_idx = ctd_deltas.idxmax()
max_gap_min = ctd_deltas[max_gap_idx] / 60.0
gap_start = master_times[max_gap_idx - 1]
gap_end = master_times[max_gap_idx]

print(f"Longest tracked gap duration:     {max_gap_min:.2f} minutes")
print(f"  --> Data Stopped/Surface:       {gap_start}")
print(f"  --> Data Resumed/Diving:        {gap_end}")
print("==================================================")