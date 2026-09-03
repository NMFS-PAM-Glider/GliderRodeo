# %% Import Modules
import matplotlib.pyplot as plt
import pandas as pd

# read in profiles csv from cloud
glider = 'capex987'
coords = pd.read_csv(f'gcs-mnt/nmfs-collaborative-working/2026_GliderRodeo/Data/{glider}_20260128/esd data structure/data-out/2026/{glider}-20260128/processed-L0/{glider}-20260128-delayed-profiles.csv')

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

# optional, cut off extra data points before and after rodeo
# cutoff = pd.to_datetime('2026-02-10 05:37')
# surfacing_coords = surfacing_coords[surfacing_coords['startTime'] <= cutoff]

# save to folder 
surfacing_coords.to_csv(f'GliderRodeo/data/{glider}_20260128/{glider}-20260128_GPS_timeseries.csv', index=False)


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

plt.title('Glider Surfacing Trajectory (stenella-20260128)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.grid(True, linestyle='--', alpha=0.5)

plt.gca().set_aspect('equal', adjustable='datalim') 

plt.tight_layout()
plt.show()