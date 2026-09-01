# % load modules
import pandas as pd
import xarray as xr

# % load ESD Glider processed engineering timeseries, convert to dataframe, and reset index to inlcude time as reg column
eng_time_ds = xr.open_dataset('gcs-mnt/swfscesd-glider-deployments-data-out/2026/stenella-20260128/processed-L1/stenella-20260128-delayed-eng.nc')

eng_time_df = eng_time_ds.to_dataframe()
eng_time_df = eng_time_df.reset_index()

# % extract vars of interest
vars = [
    'time', 'heading', 'pitch', 'roll', 'distance_over_ground', 'battery_voltage', 'battpos', 'amphr', 'total_amphr', 'measured_oil_volume'
]

# additional vars to add, work with Sam! 
# speed, speed through water, ballast state - c_autoballast_state, commanded climb and dive oil vol, picth commands (c and d use_pitch), digifin position, 

# additional seaglider vars, do we have these???
# Horizontal speed
# Vertical speed
# Speed (speed through water)
# East_displacement
# North_displacement
# Glide angle

eng_time = eng_time_df[vars]
eng_time = eng_time.rename(columns={'time': 'time_utc'})

# add epoch time column
epoch_seconds = eng_time['time_utc'].astype('int64') // 10**9
eng_time.insert(0, 'time', epoch_seconds)

# optional, cut off extra data points before and after rodeo
cutoff = pd.to_datetime('2026-02-10 05:37')
eng_time = eng_time[eng_time['time_utc'] <= cutoff]

# save as csv
eng_time.to_csv('GliderRodeo/data/stenella-20260128/stenella-20260128_engineering.csv', index=False)
