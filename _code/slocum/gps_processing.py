# %% Import Modules
import matplotlib.pyplot as plt
import pandas as pd

# set global vars
GLIDER = 'capex987'
START_TIME_CUTOFF = '2026-01-29 00:50:00'  # Format: 'YYYY-MM-DD HH:MM:SS'
END_TIME_CUTOFF = '2026-02-10 09:45:00'    # Format: 'YYYY-MM-DD HH:MM:SS'

# read in profiles csv from cloud
coords = pd.read_csv(f'gcs-mnt/nmfs-collaborative-working/2026_GliderRodeo/Data/{GLIDER}_20260128/esd data structure/data-out/2026/{GLIDER}-20260128/processed-L0/{GLIDER}-20260128-delayed-profiles.csv')
# coords = pd.read_csv(f'gcs-mnt/swfscesd-glider-deployments-data-out/2026/{GLIDER}-20260128/processed-L0/{GLIDER}-20260128-delayed-profiles.csv')

# subset variables of interest and rename
surfacing_coords = coords.loc[
    coords['profile_phase'] == 'surfacing', 
    ['start_time', 'end_time', 'min_lat', 'min_lon']
].rename(columns={ 'start_time': 'startTime', 'end_time': 'endTime', 'min_lon': 'longitude', 'min_lat': 'latitude'})

# clean times 
surfacing_coords['startTime'] = surfacing_coords['startTime'].str.strip()
surfacing_coords['startTime'] = pd.to_datetime(surfacing_coords['startTime'])

surfacing_coords['endTime'] = surfacing_coords['endTime'].str.strip()
surfacing_coords['endTime'] = pd.to_datetime(surfacing_coords['endTime'])

# only keep data between cutoff_start and cutoff_end
cutoff_start = pd.to_datetime(START_TIME_CUTOFF)
cutoff_end = pd.to_datetime(END_TIME_CUTOFF)

surfacing_coords = surfacing_coords[
    (surfacing_coords['startTime'] >= cutoff_start) & 
    (surfacing_coords['startTime'] <= cutoff_end)
]

# save
surfacing_coords.to_csv(f'GliderRodeo/data/{GLIDER}_20260128/{GLIDER}-20260128_GPS_timeseries.csv', index=False)

# %% FOR TESTING
surfacing_coords = surfacing_coords.sort_values(by='startTime')

plt.figure(figsize=(8, 6))
plt.plot(
    surfacing_coords['longitude'], 
    surfacing_coords['latitude'], 
    marker='o',       # Adds a dot for every surfacing event
    linestyle='-',    # Connects the dots with a line to show the path
    color='b',        # Blue color
    alpha=0.7         # Slight transparency
)

plt.title(f'Glider Surfacing Trajectory ({GLIDER}-20260128)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True, linestyle='--', alpha=0.5)

plt.gca().set_aspect('equal', adjustable='datalim') 

plt.tight_layout()
plt.show()