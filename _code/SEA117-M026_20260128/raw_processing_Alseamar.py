# %% load packages
import glob
import gzip
import math
import os

import gsw
import pandas as pd

# %% data directories
INPUT_DIR = "gcs-mnt/nmfs-collaborative-working/2026_GliderRodeo/Data/SEA117-MO26_20260128/0_RawData_gli_and_pld/" 

GLI_OUTPUT = "GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128_RAW_eng_timeseries.csv"
PLD_OUTPUT = "GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128_RAW_sci_timeseries.csv"

# %% set up eng and sci sheet structures
# columns from GLI spreadsheet
GLI_COLUMNS = [
    "YO_NUMBER", "Timestamp", "NavState", "SecurityLevel", "Heading", "Declination", "Pitch", "Roll", "Depth", "PressureNav", "PressureRel", "Temperature", "Pa", "Humidity", "Lat", "Lon", "DeadReckoning", "DesiredH", "DesiredHCC", "BallastCmd", "BallastPos", "LinCmd", "LinPos", "AngCmd", "AngPos", "Voltage", "Altitude"
]

# columns from PLD spreadsheet
PLD_COLUMNS = [
    "YO_NUMBER", "PLD_REALTIMECLOCK", "NAV_RESOURCE", "NAV_LONGITUDE", "NAV_LATITUDE", "NAV_DEPTH", "NAV_HEADING", "SD_CARD_USAGE", "SSD_USAGE", "ACQUISITION_FREQ", "RECORDING", "DC_count", "DC_score", "DC_azim", "DC_azim_std", "DW_count", "DW_score", "DW_azim", "DW_azim_std", "FW_count", "FW_score", "FW_azim",  "FW_azim_std", "HBW_count", "HBW_score", "HBW_azim", "HBW_azim_std", "SW_count", "SW_score", "SW_azim", "SW_azim_std", "AURIS_AN_31_Hz", "AURIS_AN_39_Hz", "AURIS_AN_50_Hz", "AURIS_AN_62_Hz", "AURIS_AN_79_Hz", "AURIS_AN_99_Hz", "AURIS_AN_125_Hz", "AURIS_AN_157_Hz", "AURIS_AN_198_Hz", "AURIS_AN_250_Hz", "AURIS_AN_315_Hz","AURIS_AN_397_Hz", "AURIS_AN_500_Hz", "AURIS_AN_630_Hz", "AURIS_AN_794_Hz", "AURIS_AN_1000_Hz", "AURIS_AN_1260_Hz", "AURIS_AN_1587_Hz", "AURIS_AN_2000_Hz", "AURIS_AN_2520_Hz", "AURIS_AN_3175_Hz", "AURIS_AN_4000_Hz", "AURIS_AN_5040_Hz", "AURIS_AN_6350_Hz", "AURIS_AN_8000_Hz", "AURIS_AN_10079_Hz", "AURIS_AN_12699_Hz", "AURIS_AN_16000_Hz", "AURIS_AN_20159_Hz", "AURIS_AN_25398_Hz", "AURIS_AN_32000_Hz", "LEGATO_CONDUCTIVITY", "LEGATO_TEMPERATURE", "LEGATO_PRESSURE", "LEGATO_SALINITY", "LEGATO_CONDTEMP", "LEGATO_SOUND_VELOCITY", "LEGATO_POTENTIAL_DENSITY"
]

# %% process raw gli data (eng)
gli_search_pattern = os.path.join(INPUT_DIR, "*.gli.sub.*.gz")
gli_gz_files = glob.glob(gli_search_pattern)

gli_data = []

for filepath in gli_gz_files:
    filename = os.path.basename(filepath)
    
    try:
        yo_number = filename.split('.')[4] 
    except IndexError:
        print(f"Warning: Could not parse YO_NUMBER from {filename}. Skipping.")
        continue
    
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        for line in f:
            clean_line = line.strip()
            if not clean_line:
                continue
                
            parts = clean_line.split(';')
            
            if parts and parts[-1] == '':
                parts.pop()
            
            if parts[0] == 'Timestamp':
                continue
                
            if len(parts) == 26:
                final_row = [yo_number] + parts
                gli_data.append(final_row)

# conver to dataframe and save as csv
gli_df = pd.DataFrame(gli_data, columns=GLI_COLUMNS)
gli_df.to_csv(GLI_OUTPUT, index=False)

# %% process raw pld data (sci)
# helper function for geographic conversion during PLD processing
def nmea_to_dd(nmea_val):
    if not nmea_val or float(nmea_val) == 0:
        return 0.0
    val = float(nmea_val)
    abs_val = abs(val)
    degrees = math.floor(abs_val / 100)
    minutes = abs_val - (degrees * 100)
    decimal_degrees = degrees + (minutes / 60.0)
    return decimal_degrees if val > 0 else -decimal_degrees

pld_search_pattern = os.path.join(INPUT_DIR, "*.pld*.raw.*.gz") 
pld_gz_files = glob.glob(pld_search_pattern)

pld_data = [] 

for filepath in pld_gz_files:
    filename = os.path.basename(filepath)
    
    try:
        yo_number = filename.split('.')[4] 
    except IndexError:
        yo_number = "Unknown"
    
    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
        for line in f:
            clean_line = line.strip()
            if not clean_line: continue
                
            parts = clean_line.split(';')
            if parts and parts[-1] == '':
                parts.pop()
            
            if parts[0] == 'PLD_REALTIMECLOCK':
                continue
                
            if len(parts) >= 66:
                parsed_data = parts[:66] 
                
                try:
                    lon = nmea_to_dd(parsed_data[2])
                    lat = nmea_to_dd(parsed_data[3])
                    
                    t = float(parsed_data[62]) if parsed_data[62] else 0.0
                    p = float(parsed_data[63]) if parsed_data[63] else 0.0
                    sp = float(parsed_data[64]) if parsed_data[64] else 0.0
                    sa = gsw.SA_from_SP(sp, p, lon, lat)
                    ct = gsw.CT_from_t(sa, t, p)
                    
                    sound_velocity = gsw.sound_speed(sa, ct, p)
                    potential_density = gsw.rho(sa, ct, 0)
                    sv_str = f"{sound_velocity:.2f}"
                    pd_str = f"{potential_density:.2f}"
                    
                except ValueError:
                    sv_str = ""
                    pd_str = ""
                    
                final_row = [yo_number] + parsed_data + [sv_str, pd_str]
                
                # Replace empty fields with 9999 to match formatting
                final_row = [val if val != '' else '9999' for val in final_row]
                pld_data.append(final_row)

# convert to dataframe and save as csv
pld_df = pd.DataFrame(pld_data, columns=PLD_COLUMNS)
pld_df.to_csv(PLD_OUTPUT, index=False) 