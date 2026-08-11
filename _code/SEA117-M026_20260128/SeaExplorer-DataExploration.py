# Processing Seaexplorer data with PyGlider (KB pyglider edited version)
# %% setup
import logging
import os
import xarray as xr
import pyglider.seaexplorer as seaexplorer
import pyglider.ncprocess as ncprocess
import importlib
import polars as pl
import matplotlib.pyplot as plt

importlib.reload(seaexplorer)
print("USING PYGLIDER FROM:", seaexplorer.__file__)

logging.basicConfig(level='INFO')

sourcedir = r"C:\Users\kourtney.burger\Documents\GitHub\GliderRodeo\data\seaexplorer"

rawdir         = os.path.join(sourcedir, 'realtime_raw') + os.sep
rawncdir       = os.path.join(sourcedir, 'realtime_rawnc') + os.sep
deploymentyaml = os.path.join(sourcedir, 'deployment.yaml') # Ensure this is .yml or .yaml matching your file
l0tsdir        = os.path.join(sourcedir, 'L0-timeseries') + os.sep
profiledir     = os.path.join(sourcedir, 'L0-profiles') + os.sep
griddir        = os.path.join(sourcedir, 'L0-gridfiles') + os.sep

# %% PyGlider processing
## convert raw files to parquet
seaexplorer.raw_to_rawnc(
    indir=rawdir,
    outdir=rawncdir,
    deploymentyaml=deploymentyaml,
    incremental=True,
    min_samples_in_file=5,
    dropna_subset=['LEGATO_TEMPERATURE'],  # Updated for your sensor
    dropna_thresh=1)

# # create datafiles with only subset of pld files
# seaexplorer.merge_parquet(rawncdir, rawncdir, deploymentyaml, kind='sub')
# timeseries = seaexplorer.raw_to_timeseries(rawncdir, l0tsdir, deploymentyaml, kind='sub')

# create datafiles with only raw pld files
seaexplorer.merge_parquet(rawncdir, rawncdir, deploymentyaml, kind='raw')
timeseries = seaexplorer.raw_to_timeseries(rawncdir, l0tsdir, deploymentyaml, kind='raw')

# %% Crop data to mission dates
# Open the dataset, drop pre- and post-mission rows, and save over the original file
logging.info('Cropping dataset strictly to mission dates')
with xr.open_dataset(timeseries) as ds:
    # Format: 'YYYY-MM-DDTHH:MM:SS'
    ds_cropped = ds.sel(time=slice('2026-01-28T21:59:00', '2026-02-11T21:59:00')).load()

# Overwrite the original NetCDF file with the truncated version
ds_cropped.to_netcdf(timeseries)

# Profile extraction and gridding
ncprocess.extract_timeseries_profiles(timeseries, profiledir, deploymentyaml)

gridfiles = ncprocess.make_gridfiles(timeseries, griddir, deploymentyaml)

# # %% extract gps data 
# nc_file = r"C:\Users\kourtney.burger\Documents\GitHub\GliderRodeo\data\seaexplorer\L0-timeseries\SEA117.26.nc"
# ds = xr.open_dataset(nc_file)

# df_gps = ds[['latitude', 'longitude', 'depth']].to_dataframe().reset_index()

# df_gps = df_gps.dropna(subset=['latitude', 'longitude', 'depth'])

# %% test plot 
# Load your new dataset
nc_file = r"C:\Users\kourtney.burger\Documents\GitHub\GliderRodeo\data\seaexplorer\L0-timeseries\SEA117.26.nc"
ds = xr.open_dataset(nc_file)

plt.figure(figsize=(12, 5))
# Plot time on X, depth on Y, and color by temperature
sc = plt.scatter(ds['time'], ds['depth'], c=ds['temperature'], cmap='jet', s=1)

plt.colorbar(sc, label='Temperature (°C)')
plt.gca().invert_yaxis()  # Put ocean surface at the top
plt.title('SEA117.26 - Water Temperature Cross-Section')
plt.xlabel('Date/Time')
plt.ylabel('Depth (m)')
plt.show()