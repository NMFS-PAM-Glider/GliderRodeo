# %% load packages and read in data
import math
import numpy as np
import pandas as pd


# helper function for processing gps strings
def nmea_to_dd(nmea_val):
    if pd.isna(nmea_val) or not nmea_val or float(nmea_val) == 0:
        return np.nan 
    val = float(nmea_val)
    abs_val = abs(val)
    degrees = math.floor(abs_val / 100)
    minutes = abs_val - (degrees * 100)
    decimal_degrees = degrees + (minutes / 60.0)
    return decimal_degrees if val > 0 else -decimal_degrees

# read in data
eng = pd.read_csv("GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128_RAW_eng_timeseries.csv")
sci = pd.read_csv("GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128_RAW_sci_timeseries.csv")

# remove extra data before and after rodeo
START_TIME_CUTOFF = '2026-01-28 21:40:00'
END_TIME_CUTOFF = '2026-02-10 06:15:00' 

cutoff_start = pd.to_datetime(START_TIME_CUTOFF)
cutoff_end = pd.to_datetime(END_TIME_CUTOFF)

eng['Timestamp'] = pd.to_datetime(eng['Timestamp'], dayfirst=True)
eng = eng[
    (eng['Timestamp'] >= cutoff_start) & 
    (eng['Timestamp'] <= cutoff_end)
]

sci['PLD_REALTIMECLOCK'] = pd.to_datetime(sci['PLD_REALTIMECLOCK'], dayfirst=True)
sci = sci[
    (sci['PLD_REALTIMECLOCK'] >= cutoff_start) & 
    (sci['PLD_REALTIMECLOCK'] <= cutoff_end)
]

# %% GPS timeseries
# extract coordinates from eng
eng['DeadReckoning'] = pd.to_numeric(eng['DeadReckoning'], errors='coerce')
eng['Lat'] = pd.to_numeric(eng['Lat'], errors='coerce')
eng['Lon'] = pd.to_numeric(eng['Lon'], errors='coerce')
eng['Depth'] = pd.to_numeric(eng['Depth'], errors='coerce')

surface_df = eng[(eng['DeadReckoning'] == 0)].copy()

surface_df['Lat_DD'] = surface_df['Lat'].apply(nmea_to_dd)
surface_df['Lon_DD'] = surface_df['Lon'].apply(nmea_to_dd)

surface_coords = surface_df[['YO_NUMBER', 'Timestamp', 'Lat_DD', 'Lon_DD']].copy()
surface_coords = surface_coords.rename(columns={'YO_NUMBER':'yo_number','Timestamp': 'time_utc', 'Lat_DD':'latitude', 'Lon_DD':'longitude'})

surface_coords = surface_coords[(surface_coords['latitude'] != 0) & (surface_coords['longitude'] != 0)]

surface_coords = surface_coords.sort_values(by=['yo_number', 'time_utc'])

# drop duplicates based on YO_NUMBER
surface_coords = surface_coords.drop_duplicates(subset=['yo_number'], keep='first')

# save timeseries
surface_coords.to_csv('GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128_GPS_timeseries.csv', index=False)

# extract dead reckoned/interpolated coordinates from eng
dr_coords = eng[(eng['DeadReckoning'] == 1)].copy()

dr_coords['Lat_DD'] = dr_coords['Lat'].apply(nmea_to_dd)
dr_coords['Lon_DD'] = dr_coords['Lon'].apply(nmea_to_dd)

dr_coords = dr_coords[['YO_NUMBER', 'Timestamp', 'Lat_DD', 'Lon_DD']].copy()
dr_coords = dr_coords.rename(columns={'YO_NUMBER':'yo_number', 'Timestamp': 'time_utc', 'Lat_DD':'latitude', 'Lon_DD':'longitude'})

dr_coords = dr_coords[(dr_coords['latitude'] != 0) & (dr_coords['longitude'] != 0)]

dr_coords = dr_coords.sort_values(by=['yo_number', 'time_utc'])

# Drop duplicates based on TIME
dr_coords = dr_coords.drop_duplicates(subset=['time_utc'], keep='first')

dr_coords.to_csv('GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128_dead-reckoned_timeseries.csv', index=False)

# %% eng timeseries
eng_clean = eng.drop(columns='SecurityLevel').copy()

eng_clean = eng_clean.rename(columns={'Timestamp': 'Time_UTC'})

# map numeric NavState codes to descriptions
nav_state_mapping = {
    110: 'inflecting down',
    100: 'descent',
    118: 'inflecting up',
    117: 'ascent',
    115: 'surfacing',
    119: 'gps',
    116: 'transmitting',
    123: 'ballasting',
    124: 'drifting'
}
eng_clean['NavState'] = eng_clean['NavState'].replace(nav_state_mapping)

# add epoch time column
epoch = (eng_clean['Time_UTC'] - pd.Timestamp("1970-01-01")).dt.total_seconds()
eng_clean.insert(0, 'Time', epoch)

# convert NMEA coordinates to decimal degrees
eng_clean['Lat'] = eng_clean['Lat'].apply(nmea_to_dd)
eng_clean['Lon'] = eng_clean['Lon'].apply(nmea_to_dd)

# save csv
eng_clean.to_csv('GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128_flight_timeseries_engineering.csv', index=False)

# %% sci timeseries
sci_vars = ['YO_NUMBER', 'PLD_REALTIMECLOCK', 'NAV_RESOURCE', 'NAV_LONGITUDE', 'NAV_LATITUDE', 'NAV_DEPTH', 'NAV_HEADING', 'SD_CARD_USAGE', 'SSD_USAGE', 'LEGATO_CONDUCTIVITY', 'LEGATO_TEMPERATURE', 'LEGATO_PRESSURE', 'LEGATO_SALINITY', 'LEGATO_CONDTEMP', 'LEGATO_SOUND_VELOCITY', 'LEGATO_POTENTIAL_DENSITY']

sci_clean = sci[sci_vars].copy()

sci_clean = sci_clean.rename(columns={'PLD_REALTIMECLOCK': 'Time_UTC', 'NAV_RESOURCE':'NAV_STATE'})

# map numeric NavState codes to descriptions
sci_clean['NAV_STATE'] = sci_clean['NAV_STATE'].replace(nav_state_mapping)

# add epoch time column
epoch = (sci_clean['Time_UTC'] - pd.Timestamp("1970-01-01")).dt.total_seconds()
sci_clean.insert(0, 'Time', epoch)

# remove 9999 and add nas
sci_clean = sci_clean.replace([9999, 9999.0, '9999'], np.nan)

# forward filling nav_state and interpolating depth
sci_clean['NAV_STATE'] = sci_clean['NAV_STATE'].ffill().bfill()

sci_clean['NAV_DEPTH'] = pd.to_numeric(sci_clean['NAV_DEPTH'], errors='coerce')
sci_clean['NAV_DEPTH'] = sci_clean['NAV_DEPTH'].interpolate(method='linear')

# convert NMEA coordinates to decimal degrees
sci_clean['NAV_LATITUDE'] = pd.to_numeric(sci_clean['NAV_LATITUDE'], errors='coerce')
sci_clean['NAV_LONGITUDE'] = pd.to_numeric(sci_clean['NAV_LONGITUDE'], errors='coerce')

sci_clean['NAV_LATITUDE'] = sci_clean['NAV_LATITUDE'].apply(nmea_to_dd)
sci_clean['NAV_LONGITUDE'] = sci_clean['NAV_LONGITUDE'].apply(nmea_to_dd)

# save csv
sci_clean.to_csv('GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128_science_timeseries.csv', index=False)