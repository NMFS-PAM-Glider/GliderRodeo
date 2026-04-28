# Cleaning Seaexplorer data with PyGlider (Alseamar)

# setting up python env 
# Setting up pyglider - only do this once per machine 
# 1. open terminal and run the following commands 
# conda create -n gliderwork # save this locally
# conda activate gliderwork
# conda install -c conda-forge pyglider
# 2. Select the New Environment in Positron
# 2.1. Open the Command Palette by pressing Ctrl+Shift+P 
# 2.2. Type in Python: Select Interpreter and select it from the dropdown list. You should see a list of available Python environments. Look for the one named gliderwork (it will likely have conda in the path) and click on it

# FOR TESTING - get example data from pyglider example repo here - https://github.com/c-proof/pyglider-example-data/tree/main/example-seaexplorer 

# Should be able to run these two lines but getting 404 error 
# import pyglider.example_data as pexamp
# pexamp.get_example_data('./')


# Example processing script
import logging
import os
import pyglider.seaexplorer as seaexplorer
import pyglider.ncprocess as ncprocess
import pyglider.utils as pgutils

logging.basicConfig(level='INFO')

# 1. Point to the specific example-seaexplorer folder you downloaded
base_dir = r"C:\Users\kourtney.burger\Documents\GitHub\GliderRodeo\data\example-seaexplorer"

# 2. Set directories (CRITICAL FIX: PyGlider explicitly requires trailing slashes)
rawdir         = os.path.join(base_dir, 'realtime_raw') + '/'
rawncdir       = os.path.join(base_dir, 'realtime_rawnc') + '/'
deploymentyaml = os.path.join(base_dir, 'deploymentRealtime.yml')
l0tsdir        = os.path.join(base_dir, 'L0-timeseries') + '/'
profiledir     = os.path.join(base_dir, 'L0-profiles') + '/'
griddir        = os.path.join(base_dir, 'L0-gridfiles') + '/'
plot_file      = os.path.join(base_dir, 'gridplot.png')

# Create the output directories if they don't exist yet
for d in [rawncdir, l0tsdir, profiledir, griddir]:
    os.makedirs(d, exist_ok=True)

# 3. Clean last processing (Cross-platform Python method)
def clean_directory(directory_path):
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

clean_directory(rawncdir)
clean_directory(l0tsdir)
clean_directory(profiledir)
clean_directory(griddir)

# 4. Process the data
if True:
    # Turn *.EBD and *.DBD into *.ebd.nc and *.dbd.nc netcdf files
    seaexplorer.raw_to_rawnc(rawdir, rawncdir, deploymentyaml)
    
    # Merge individual netcdf files into single netcdf files *.ebd.nc and *.dbd.nc
    seaexplorer.merge_parquet(rawncdir, rawncdir, deploymentyaml, kind='sub')

    # Make level-1 timeseries netcdf file from the raw files
    outname = seaexplorer.raw_to_timeseries(rawncdir, l0tsdir, deploymentyaml, kind='sub')
    
    # Extract profiles
    ncprocess.extract_timeseries_profiles(outname, profiledir, deploymentyaml)
    
    # Make grid files
    outname2 = ncprocess.make_gridfiles(outname, griddir, deploymentyaml)

    # Generate the plot and save it to your folder
    pgutils.example_gridplot(outname2, plot_file, ylim=[700, 0],
                             toplot=['potential_temperature', 'salinity', 'oxygen_concentration',
                                     'chlorophyll', 'cdom'])
    
    print(f"Processing complete! Check {base_dir} for your new files and gridplot.png.")




## EXTRACTING SCIENCE TIMESTAMPS FROM pld1.raw FILES
import pandas as pd
import glob
import os

# Point this to the folder containing your compressed pld1 files
data_folder = r"E:\alseamar\_KB files\PyGliderTesting\delayed_raw"

# Search specifically for the .gz compressed payload files
pld_files = glob.glob(os.path.join(data_folder, "*.pld1.*.gz"))

if not pld_files:
    print(f"No compressed .pld1.gz files found in {data_folder}")
else:
    print(f"Found {len(pld_files)} compressed payload files. Extracting timestamps directly from gzip...")
    
    all_data = []
    for file in pld_files:
        try:
            # Added compression='gzip' so pandas unzips it on the fly!
            df = pd.read_csv(file, sep=';', on_bad_lines='skip', low_memory=False, compression='gzip')
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if all_data:
        # Combine all the files into one big table
        science_df = pd.concat(all_data, ignore_index=True)
        
        # Check if the standard SeaExplorer time column exists
        time_col = 'PLD_REALTIMECLOCK'
        
        if time_col not in science_df.columns:
            # Fallback just in case your glider software named it something else
            print(f"Couldn't find '{time_col}'. Here are the columns I did find:")
            print(science_df.columns.tolist())
        else:
            # Convert the text timestamps into actual Python datetime objects
            science_df['Datetime'] = pd.to_datetime(science_df[time_col], format='mixed', dayfirst=True, errors='coerce')
            
            # Drop any rows where the timestamp was corrupted
            valid_times = science_df.dropna(subset=['Datetime'])
            
            # Sort the data chronologically
            valid_times = valid_times.sort_values(by='Datetime')
            
            # --- Print the Summary ---
            start_time = valid_times['Datetime'].iloc[0]
            end_time = valid_times['Datetime'].iloc[-1]
            total_measurements = len(valid_times)
            
            print("\n" + "="*40)
            print("🌊 SCIENCE DATA TIMELINE SUMMARY 🌊")
            print("="*40)
            print(f"First measurement: {start_time}")
            print(f"Last measurement:  {end_time}")
            print(f"Total data points: {total_measurements:,}")
            
            print("\n📅 Measurements per day:")
            # Group by just the date (ignore the exact time) and count them up
            daily_counts = valid_times['Datetime'].dt.date.value_counts().sort_index()
            print(daily_counts.to_string())
            print("="*40)




### EXTRACTING CTD DATA 
import pandas as pd
import glob
import os

# Point this to your folder containing the compressed pld1 files
data_folder = r"E:\alseamar\_KB files\PyGliderTesting\delayed_raw"
output_file = os.path.join(data_folder, "extracted_CTD_data.csv")

# Search specifically for the .gz compressed payload files
pld_files = glob.glob(os.path.join(data_folder, "*.pld1.*.gz"))

if not pld_files:
    print(f"No compressed .pld1.gz files found in {data_folder}")
else:
    print(f"Found {len(pld_files)} payload files. Loading data...")
    
    all_data = []
    for file in pld_files:
        try:
            # Read and decompress on the fly
            df = pd.read_csv(file, sep=';', on_bad_lines='skip', low_memory=False, compression='gzip')
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if all_data:
        # Combine into one master dataframe
        science_df = pd.concat(all_data, ignore_index=True)
        
        # 1. Identify the Time column
        time_col = 'PLD_REALTIMECLOCK'
        if time_col not in science_df.columns:
            print(f"Error: Could not find '{time_col}'.")
        else:
            # 2. Automatically find the CTD columns
            # We look for standard abbreviations for Temperature, Conductivity, and Pressure
            ctd_columns = [col for col in science_df.columns if 
                           'TEMP' in col.upper() or 
                           'COND' in col.upper() or 
                           'PRES' in col.upper()]
            
            print(f"\nIdentified the following CTD columns: {ctd_columns}")
            
            # Combine Time + CTD columns into our final list
            columns_to_keep = [time_col] + ctd_columns
            
            # 3. Extract just the columns we want
            ctd_data = science_df[columns_to_keep].copy()
            
            # 4. Clean up the timestamps
            print("\nFormatting timestamps and sorting data...")
            ctd_data['Datetime'] = pd.to_datetime(ctd_data[time_col], format='mixed', dayfirst=True, errors='coerce')
            
            # Drop rows with corrupted timestamps or where ALL CTD data is missing
            ctd_data = ctd_data.dropna(subset=['Datetime'])
            ctd_data = ctd_data.dropna(subset=ctd_columns, how='all')
            
            # Sort chronologically and drop the old text-based time column
            ctd_data = ctd_data.sort_values(by='Datetime')
            ctd_data = ctd_data.drop(columns=[time_col])
            
            # Reorder so Datetime is the first column
            cols = ['Datetime'] + ctd_columns
            ctd_data = ctd_data[cols]
            
            # 5. Save and display
            ctd_data.to_csv(output_file, index=False)
            
            print("\n" + "="*50)
            print("✅ EXTRACTION COMPLETE")
            print("="*50)
            print(f"Total CTD measurements: {len(ctd_data):,}")
            print(f"Clean data saved to: {output_file}")
            print("\nPreview of your extracted data:")
            print(ctd_data.head())



### EXTRACT COORDINATE FROM PAYLOAD - 
import pandas as pd
import glob
import os

# 1. Setup paths
data_folder = r"E:\alseamar\_KB files\PyGliderTesting\delayed_raw"
output_file = os.path.join(data_folder, "extracted_navigation_estimates.csv")

# 2. Find all compressed pld1 files
pld_files = glob.glob(os.path.join(data_folder, "*.pld1.*.gz"))

if not pld_files:
    print(f"No compressed .pld1.gz files found in {data_folder}")
else:
    print(f"Found {len(pld_files)} payload files. Extracting navigation data...")
    
    all_nav_data = []
    
    for file in pld_files:
        try:
            # We only load the columns we need to save memory and time
            # Using usecols tells pandas exactly which headers to grab
            cols_to_read = ['PLD_REALTIMECLOCK', 'NAV_LATITUDE', 'NAV_LONGITUDE', 'NAV_DEPTH']
            
            df = pd.read_csv(file, 
                             sep=';', 
                             usecols=cols_to_read, 
                             compression='gzip', 
                             on_bad_lines='skip')
            
            all_nav_data.append(df)
        except ValueError:
            # This happens if one of the columns (like NAV_LATITUDE) is missing in a specific file
            print(f"Skipping {os.path.basename(file)}: Missing nav columns.")
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if all_nav_data:
        # Combine all files
        nav_df = pd.concat(all_nav_data, ignore_index=True)
        
        # 3. Format timestamps
        print("Formatting timestamps...")
        nav_df['Datetime'] = pd.to_datetime(nav_df['PLD_REALTIMECLOCK'], format='mixed', dayfirst=True, errors='coerce')
        
        # Drop rows with broken timestamps or missing GPS estimates
        nav_df = nav_df.dropna(subset=['Datetime', 'NAV_LATITUDE', 'NAV_LONGITUDE'])
        
        # Sort by time
        nav_df = nav_df.sort_values(by='Datetime')
        
        # Reorder columns for a clean CSV
        final_df = nav_df[['Datetime', 'NAV_LATITUDE', 'NAV_LONGITUDE', 'NAV_DEPTH']]
        
        # 4. Save to CSV
        final_df.to_csv(output_file, index=False)
        
        print("\n" + "="*50)
        print("✅ NAVIGATION EXTRACTION COMPLETE")
        print("="*50)
        print(f"File saved to: {output_file}")
        print(f"Total points extracted: {len(final_df):,}")
        print("\nFirst 5 rows:")
        print(final_df.head())
    else:
        print("No navigation data was extracted.")


import pandas as pd
import plotly.express as px
import os

# 1. Paths
file_path = r"E:\alseamar\_KB files\PyGliderTesting\delayed_raw\extracted_navigation_estimates.csv"

def convert_seaexplorer_coords(coord):
    """Converts DDMM.mmmm to Decimal Degrees (DD.dddd)"""
    if pd.isna(coord) or coord == 0:
        return None
    # SeaExplorer format is often DDMM.mmmm
    # We take the last two digits of the whole number as minutes
    degrees = int(coord / 100)
    minutes = coord - (degrees * 100)
    return degrees + (minutes / 60)

if not os.path.exists(file_path):
    print("Error: CSV not found!")
else:
    df = pd.read_csv(file_path)
    
    # --- CRITICAL FIX: Convert coordinates if they are in DDMM format ---
    # Check if the first value is > 90 (which means it's definitely not decimal degrees)
    if df['NAV_LATITUDE'].abs().max() > 90:
        print("Detected SeaExplorer DDMM format. Converting to Decimal Degrees...")
        df['NAV_LATITUDE'] = df['NAV_LATITUDE'].apply(convert_seaexplorer_coords)
        df['NAV_LONGITUDE'] = df['NAV_LONGITUDE'].apply(convert_seaexplorer_coords)
        # Flip longitude to negative if you are in the Western Hemisphere (e.g., North America)
        # Most SeaExplorers report positive Longitude for West; Python needs negative.
        if df['NAV_LONGITUDE'].mean() > 0: 
             df['NAV_LONGITUDE'] = df['NAV_LONGITUDE'] * -1

    # Drop any rows that failed conversion
    df = df.dropna(subset=['NAV_LATITUDE', 'NAV_LONGITUDE'])

    print(f"Plotting {len(df)} points...")
    print(df[['NAV_LATITUDE', 'NAV_LONGITUDE']].head()) # Sanity check the numbers

    # 2. Try 'scatter_mapbox' (Sometimes more stable than scatter_map in older plotly versions)
    fig = px.scatter_mapbox(
        df, 
        lat="NAV_LATITUDE", 
        lon="NAV_LONGITUDE", 
        color="NAV_DEPTH",
        hover_data=["Datetime"],
        zoom=7,
        height=800,
        title="SeaExplorer Track"
    )

    fig.update_layout(
        mapbox_style="open-street-map", 
        margin={"r":0,"t":40,"l":0,"b":0}
    )

    fig.show()