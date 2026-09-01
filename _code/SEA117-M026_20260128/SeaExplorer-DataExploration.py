import xarray as xr

ds_raw = xr.load_dataset("data/SEA117-M026_20260128/L0-profiles/SEA117117-20260202T0311.nc")
df = ds_raw.to_dataframe()
