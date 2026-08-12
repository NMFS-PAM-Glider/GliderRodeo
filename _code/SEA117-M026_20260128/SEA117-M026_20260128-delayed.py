import logging
import os
import pyglider.seaexplorer as seaexplorer
import pyglider.ncprocess as ncprocess
import pyglider.utils as pgutils

logging.basicConfig(
    filename= "C:/Users/kourtney.burger/Documents/GitHub/GliderRodeo/data/SEA117-M026_20260128/SEA117-M026_20260128-processing.log",
    filemode="w",
    format="%(name)s:%(asctime)s:%(levelname)s:%(message)s [line %(lineno)d]",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.captureWarnings(True)
logging.info("Beginning scheduled processing")

# sourcedir = '~alseamar/Documents/SEA035/000012/000012/C-Csv/*'
rawdir  = 'data/SEA117-M026_20260128/0_RawData_gli_and_pld_sub/'
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
    seaexplorer.merge_parquet(rawncdir, rawncdir, deploymentyaml, kind='sub')

    # Make level-1 timeseries netcdf file from the raw files...
    outname = seaexplorer.raw_to_timeseries(rawncdir, l0tsdir, deploymentyaml, kind='sub')
    # ncprocess.extract_timeseries_profiles(outname, profiledir, deploymentyaml)
    # outname2 = ncprocess.make_gridfiles(outname, griddir, deploymentyaml)

    # pgutils.example_gridplot(outname2, './gridplot.png', ylim=[700, 0],
    #                          toplot=['potential_temperature', 'salinity', 'oxygen_concentration',
    #                                  'chlorophyll', 'cdom'])
