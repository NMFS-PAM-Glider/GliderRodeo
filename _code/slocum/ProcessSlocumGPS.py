# %% Import Modules
import matplotlib.pyplot as plt
import pandas as pd

# read in profiles csv
coords = pd.read_csv('gcs-mnt/nmfs-collaborative-working/2026_GliderRodeo/Data/SEA117-MO26_20260128//processed-L0/risso-20260128-delayed-profiles.csv')

# subset variables of interest and rename
surfacing_coords = coords.loc[
    coords['profile_phase'] == 'surfacing', 
    ['start_time', 'end_time', 'min_lat', 'min_lon']
].rename(columns={'min_lon': 'Longitude', 'min_lat': 'Latitude'})

# clean times 
surfacing_coords['start_time'] = surfacing_coords['start_time'].str.strip()
surfacing_coords['start_time'] = pd.to_datetime(surfacing_coords['start_time'])

# optional, cut off extra data points before and after rodeo
cutoff = pd.to_datetime('2026-02-10 05:37')
surfacing_coords = surfacing_coords[surfacing_coords['start_time'] <= cutoff]

# save to folder 
surfacing_coords.to_csv('GliderRodeo/data/risso-20260128/risso-20260128_GPS.csv', index=False)


# %% FOR TESTING
surfacing_coords = surfacing_coords.sort_values(by='start_time')

plt.figure(figsize=(8, 6))
plt.plot(
    surfacing_coords['Longitude'], 
    surfacing_coords['Latitude'], 
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