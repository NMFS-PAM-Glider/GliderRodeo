# %% load packages
import dbdreader
import pandas as pd
import os
import pprint

#%% load flight (dcd) and sci (ecd) data
flight = dbdreader.MultiDBD(
    pattern="D:/esd data structure/data-in/2026/capex987-20260128/binary/delayed/*.dcd",
    cacheDir=r"D:\esd data structure\backup\glider-files\Flight\state\cache"
)

sci = dbdreader.MultiDBD(
    pattern="D:/esd data structure/data-in/2026/capex987-20260128/binary/delayed/*.ecd",
    cacheDir=r"D:\esd data structure\backup\glider-files\Science\state\cache"
)

#%% print list of variables in the dbd files
pprint.pprint(flight.parameterNames)

pprint.pprint(sci.parameterNames)

# %% extract timestamps with following variables, put in data frame for exploration
time, sci_water_temp, sci_rbrctd_temperature_00,  sci_water_cond, sci_rbrctd_conductivity_00, sci_water_pressure, sci_rbrctd_pressure_00 = sci.get_sync(
    "sci_water_temp", 
    "sci_rbrctd_temperature_00",
    "sci_water_cond", 
    "sci_rbrctd_conductivity_00",
    "sci_water_pressure",
    "sci_rbrctd_pressure_00"
)

df = pd.DataFrame({
    "timestamp": time,
    "sci_water_temp": sci_water_temp,
    "sci_rbrctd_temperature_00": sci_rbrctd_temperature_00,
    "sci_water_cond": sci_water_cond,
    "sci_rbrctd_conductivity_00": sci_rbrctd_conductivity_00,
    "sci_water_pressure": sci_water_pressure,
    "sci_rbrctd_pressure_00": sci_rbrctd_pressure_00
})

df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
