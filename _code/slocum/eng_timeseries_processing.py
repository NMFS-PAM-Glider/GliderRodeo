# % load modules
import pandas as pd
import xarray as xr

# set global vars
GLIDER = 'risso'
START_TIME_CUTOFF = '2026-01-28 23:15:00'  # Format: 'YYYY-MM-DD HH:MM:SS'
END_TIME_CUTOFF = '2026-02-10 09:45:00'    # Format: 'YYYY-MM-DD HH:MM:SS'

eng_time_ds = xr.open_dataset(f'gcs-mnt/swfscesd-glider-deployments-data-out/2026/{GLIDER}-20260128/processed-L0/{GLIDER}-20260128-delayed-raw.nc')

eng_time_df = eng_time_ds.to_dataframe()
eng_time_df = eng_time_df.reset_index()

# % extract vars of interest
vars = ['time', 'm_depth', 'm_heading', 'm_pitch', 'm_roll', 'm_battery', 'm_battpos', 'm_coulomb_amphr', 'm_coulomb_amphr_total', 'm_coulomb_current', 'm_de_oil_vol', 'm_gps_lat', 'm_gps_lon', 'm_depth_rate', 'm_fin', 'm_speed', 'm_speed_avg', 'c_de_oil_vol', 'c_pitch', 'c_fin', 'profile_index', 'profile_direction']

eng_time = eng_time_df[vars]
eng_time = eng_time.rename(columns={'time': 'time_utc'})

# add epoch time column
epoch_seconds = eng_time['time_utc'].astype('int64') // 10**9
eng_time.insert(0, 'time', epoch_seconds)

# only keep data between cutoff_start and cutoff_end
cutoff_start = pd.to_datetime(START_TIME_CUTOFF)
cutoff_end = pd.to_datetime(END_TIME_CUTOFF)

eng_time = eng_time[
    (eng_time['time_utc'] >= cutoff_start) & 
    (eng_time['time_utc'] <= cutoff_end)
]

# keep row with m_depth reading
eng_time = eng_time.dropna(subset=['m_depth'])

# save as csv
eng_time.to_csv(f'GliderRodeo/data/{GLIDER}_20260128/{GLIDER}-20260128_flight_timeseries_engineering.csv', index=False)
