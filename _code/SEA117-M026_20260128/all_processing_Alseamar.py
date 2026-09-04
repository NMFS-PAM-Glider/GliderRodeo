# %% Processing L0 Profile NetCDFs created with /_code/SEA117-M026_20260128/SEA117-M026_20260128-delayed.py
import xarray as xr
import pandas as pd

# %% prep data from nc files 
# file_path = "gcs-mnt/nmfs-collaborative-working/2026_GliderRodeo/Data/SEA117-MO26_20260128/L0-profiles/*.nc"

# ds = xr.open_mfdataset(
#     file_path, 
#     combine='nested', 
#     concat_dim='time',
#     data_vars='minimal',
#     coords='minimal', 
#     compat='override'
# )

# df = ds.to_dataframe().reset_index()

# profiles = df.sort_values(by='time').reset_index(drop=True)

# # Save time running above script
# profiles.to_csv('GliderRodeo/data/SEA117-M026_20260128/timeseries.csv', index=False)

# %% read in raw data
df = pd.read_csv('GliderRodeo/data/SEA117-M026_20260128/timeseries.csv')

# %% Create surface gps csv


# %% Create eng csv


# %% Create sci csv

