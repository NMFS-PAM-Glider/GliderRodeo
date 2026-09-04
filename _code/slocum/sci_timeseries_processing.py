# % load modules
import pandas as pd
import xarray as xr

# set global vars
GLIDER = 'stenella'
START_TIME_CUTOFF = '2026-01-28 20:45:00'  # Format: 'YYYY-MM-DD HH:MM:SS'
END_TIME_CUTOFF = '2026-02-10 05:40:00'    # Format: 'YYYY-MM-DD HH:MM:SS'


# % load ESD Glider processed science timeseries, convert to dataframe, and reset index to inlcude time as reg column
# sci_time_ds = xr.open_dataset(f'gcs-mnt/nmfs-collaborative-working/2026_GliderRodeo/Data/{GLIDER}_20260128/esd data structure/data-out/2026/{GLIDER}-20260128/processed-L1/{GLIDER}-20260128-delayed-sci.nc')
sci_time_ds = xr.open_dataset(f'gcs-mnt/swfscesd-glider-deployments-data-out/2026/{GLIDER}-20260128/processed-L1/{GLIDER}-20260128-delayed-sci.nc')

sci_time_df = sci_time_ds.to_dataframe()
sci_time_df = sci_time_df.reset_index()

# % extract vars of interest
vars = [
    'time', 'latitude', 'longitude', 'depth', 'conductivity', 'temperature', 
    'pressure', 'salinity', 'density', 'potential_temperature', 'potential_density'
]

sci_time = sci_time_df[vars]
sci_time = sci_time.rename(columns={'time': 'time_utc'})

# add epoch time column
epoch_seconds = sci_time['time_utc'].astype('int64') // 10**9
sci_time.insert(0, 'time', epoch_seconds)

# only keep data between cutoff_start and cutoff_end
cutoff_start = pd.to_datetime(START_TIME_CUTOFF)
cutoff_end = pd.to_datetime(END_TIME_CUTOFF)

surfacing_coords = sci_time[
    (sci_time['time_utc'] >= cutoff_start) & 
    (sci_time['time_utc'] <= cutoff_end)
]

# save as csv
sci_time.to_csv(f'GliderRodeo/data/{GLIDER}_20260128/{GLIDER}-20260128_science_timeseries.csv', index=False)
