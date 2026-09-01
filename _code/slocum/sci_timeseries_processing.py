# % load modules
import pandas as pd
import xarray as xr

# % load ESD Glider processed science timeseries, convert to dataframe, and reset index to inlcude time as reg column
sci_time_ds = xr.open_dataset('gcs-mnt/swfscesd-glider-deployments-data-out/2026/stenella-20260128/processed-L1/stenella-20260128-delayed-sci.nc')

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

# optional, cut off extra data points before and after rodeo
cutoff = pd.to_datetime('2026-02-10 05:37')
sci_time = sci_time[sci_time['time_utc'] <= cutoff]

# save as csv
sci_time.to_csv('GliderRodeo/data/stenella-20260128/stenella-20260128_science.csv', index=False)
