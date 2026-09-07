# WORK IN PROGRESS - PyGlider Processing Methods
import logging
import pyglider.seaexplorer as seaexplorer
import pyglider.ncprocess as ncprocess
import pyglider.utils as pgutils
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr

# %% Basic PyGlider processing
logging.basicConfig(
    filename= "data/SEA117-M026_20260128/SEA117-M026_20260128-processing.log",
    filemode="w",
    format="%(name)s:%(asctime)s:%(levelname)s:%(message)s [line %(lineno)d]",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.captureWarnings(True)
logging.info("Beginning scheduled processing")

# # GCS Files - linux remote workstation
# # sourcedir = '~alseamar/Documents/SEA035/000012/000012/C-Csv/*'
# rawdir  = 'gcs-mnt/nmfs-collaborative-working/2026_GliderRodeo/Data/SEA117-MO26_20260128/Raw/'
# rawncdir     = 'GliderRodeo/data/SEA117-M026_20260128/realtime_rawnc/'
# deploymentyaml = 'GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128.yaml'
# l0tsdir    = 'GliderRodeo/data/SEA117-M026_20260128/L0-timeseries/'
# profiledir = 'GliderRodeo/data/SEA117-M026_20260128/L0-profiles/'
# griddir    = 'GliderRodeo/data/SEA117-M026_20260128/L0-gridfiles/'

# Local Files - windows machine (for testing)
# sourcedir = '~alseamar/Documents/SEA035/000012/000012/C-Csv/*'
rawdir  = 'C:/Users/kourtney.burger/Documents/GitHub/GliderRodeo/data/SEA117-M026_20260128/0_RawData_gli_and_pld/'
rawncdir     = 'data/SEA117-M026_20260128/realtime_rawnc/'
deploymentyaml = 'data/SEA117-M026_20260128/SEA117-M026_20260128.yaml'
l0tsdir    = 'data/SEA117-M026_20260128/L0-timeseries/'
profiledir = 'data/SEA117-M026_20260128/L0-profiles/'
griddir    = 'data/SEA117-M026_20260128/L0-gridfiles/'

## get the data and clean up derived
# if False:
#     os.system('rsync -av ' + sourcedir + ' ' + rawdir)

# # clean last processing...
# os.system('rm ' + rawncdir + '* ' + l0tsdir + '* ' + profiledir + '* ' +
#           griddir + '* ')

if True:
    # turn *.EBD and *.DBD into *.ebd.nc and *.dbd.nc netcdf files.
    seaexplorer.raw_to_rawnc(rawdir, rawncdir, deploymentyaml)
    # merge individual neetcdf files into single netcdf files *.ebd.nc and *.dbd.nc
    seaexplorer.merge_parquet(rawncdir, rawncdir, deploymentyaml, kind='raw')

    # Make level-1 timeseries netcdf file from the raw files...
    outname = seaexplorer.raw_to_timeseries(rawncdir, l0tsdir, deploymentyaml, kind='raw')
    ncprocess.extract_timeseries_profiles(outname, profiledir, deploymentyaml)
    outname2 = ncprocess.make_gridfiles(outname, griddir, deploymentyaml)

    # pgutils.example_gridplot(outname2, './gridplot.png', ylim=[700, 0],
    #                          toplot=['potential_temperature', 'salinity', 'oxygen_concentration',
    #                                  'chlorophyll', 'cdom'])

    #--------------------------------------------------------------------------
    logging.info("Completed scheduled processing")




# %% Processing PyGlider L0 Profile NetCDFs created above
# prep data from nc files 
# time base for files is legato_temperature (payload clock)
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
# profiles.to_csv('GliderRodeo/data/SEA117-M026_20260128/raw_timeseries.csv', index=False)

# read in raw data and remove extra data
df = pd.read_csv('GliderRodeo/data/SEA117-M026_20260128/raw_timeseries.csv')

df['time'] = pd.to_datetime(df['time'])

# remove extra data before and after rodeo
START_TIME_CUTOFF = '2026-01-28 21:40:00' # Format: 'YYYY-MM-DD HH:MM:SS'
END_TIME_CUTOFF = '2026-02-10 06:15:00' # Format: 'YYYY-MM-DD HH:MM:SS'

cutoff_start = pd.to_datetime(START_TIME_CUTOFF)
cutoff_end = pd.to_datetime(END_TIME_CUTOFF)

df = df[
    (df['time'] >= cutoff_start) & 
    (df['time'] <= cutoff_end)
]

# Create surface gps csv
coord_vars = ['time', 'lat', 'lon']
coords = df[vars]
coords = coords.rename(columns={'time': 'time_utc', 'lat':'latitude', 'lon':'longitude'})

# clean data (remove na)
surfacing_coords = coords.dropna()

# save
surfacing_coords.to_csv('GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128_GPS_timeseries.csv', index=False)

# for testing
# surfacing_coords = surfacing_coords.sort_values(by='time_utc')

# plt.figure(figsize=(8, 6))
# plt.plot(
#     surfacing_coords['longitude'], 
#     surfacing_coords['latitude'], 
#     marker='o',       # Adds a dot for every surfacing event
#     linestyle='-',    # Connects the dots with a line to show the path
#     color='b',        # Blue color
#     alpha=0.7         # Slight transparency
# )

# plt.title('Glider Surfacing Trajectory (SEA117_M026-20260128)')
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')
# plt.grid(True, linestyle='--', alpha=0.5)

# plt.gca().set_aspect('equal', adjustable='datalim') 

# plt.tight_layout()
# plt.show()

# Create eng csv
eng_vars = ['time', 'heading', 'pitch', 'roll', 'distance_over_ground', 'profile_index', 'profile_direction', 'trajectory', 'latitude', 'longitude', 'depth']
coords = df[vars]
coords = coords.rename(columns={'time': 'time_utc', 'lat':'latitude', 'lon':'longitude'})

# clean data (remove na)
surfacing_coords = coords.dropna()

# save
surfacing_coords.to_csv('GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128_GPS_timeseries.csv', index=False)

# Create sci csv




