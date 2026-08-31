% SEAGLIDER_DATA_WRANGLE.M
%	Reformat seaglider data outputs for rodeo hackathon
%
%	Description:
%		Read in "standard" agate output data tables for Seagliders for the
%		WHICEAS mission data and reformat some columns to fit the desired
%		format for the hackathon and trim to just the two weeks of the
%		rodeo.
%
%       Starting data tables have time in matlab datenum or datetime
%       format. This gets changed to Unix epoch seconds (Seconds since
%       1970-0101T00:00:00+00:00, UTC) and drops original time columns.
%
%       Input files will not be accessible to the GliderRodeo repo but
%       filse are output directly there.
%
%	Notes
%
%	See also
%
%
%	Authors:
%		S. Fregosi <selene.fregosi@gmail.com> <https://github.com/sfregosi>
%
%	Updated:   2026 August 30
%
%	Created with MATLAB ver.: 24.2.0.3212159 (R2024b) Update 9
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

addpath(genpath('C:\Users\pam_user\Documents\MATLAB\agate'))
path_repo = 'C:\Users\pam_user\Documents\GitHub\GliderRodeo';

% glider strings
gliders = {'sg274', 'sg607'};

% define rodeo times
% SG274, last dive was Dive 70, last surfacing was 2/10/26 0820 UTC
% SG607, last dive was Dive 64, last surfacing was 2/10/26
lastDives = [70; 64];
lastTimes = [datetime(2026,2,10,8,20,0); datetime(2026,2,10,8,0,0)];


%% loop through gliders
for gtr = 2 %:length(gliders) % set to a number to test one glider

    glider = gliders{gtr};

    % build input path
    path_in = fullfile('C:\Users\pam_user\Desktop', ...
        [glider, '_20260128_WHICEAS'], 'piloting', 'profiles');

    % set output path
    path_out = fullfile(path_repo, 'data', [glider '_20260128']);
    if ~exist(path_out, 'dir'); mkdir(path_out); end

    % define rodeo times
    lastDive = lastDives(gtr);
    lastTime = lastTimes(gtr);

    % load agate outputs
    load(fullfile(path_in, [glider '_20260128_WHICEAS_gpsSurfaceTable.mat']));
    load(fullfile(path_in, [glider '_20260128_WHICEAS_locCalcT.mat']));
    load(fullfile(path_in, [glider '_20260128_WHICEAS_engTable.mat']));

    %trim to just the rodeo dates
    gpsSurfT(gpsSurfT.dive > lastDive, :) = [];
    locCalcT(locCalcT.dateTime > lastTime, :) = [];
    engT(engT.dateTime > lastTime, :) = [];

    % create gps timeseries
    % convert times to unix epoch time
    gpsSurfT.startTime = datenum2unix(gpsSurfT.startTime);
    gpsSurfT.endTime   = datenum2unix(gpsSurfT.endTime);
    gpsSurfT = removevars(gpsSurfT, {'startDateTime', 'endDateTime'});
    % write to CSV in repo
    writetable(gpsSurfT, fullfile(path_out, [glider '_20260128_GPS_timeseries.csv']))

    % create science timeseries
    % convert times to unix epoch time
    locCalcT.time = datenum2unix(locCalcT.time);
    locCalcT = removevars(locCalcT, 'dateTime');
    % pull just the science columns
    sciT = locCalcT(:, {'dive', 'time', 'latitude', 'longitude', 'depth', ...
    	'temperature', 'salinity', 'density', 'soundVelocity'});
    % write to CSV in repo
    writetable(sciT, fullfile(path_out, [glider '_20260128_science_timeseries.csv']))

    % create flight timeseries - there are two
    % first from locCalcT - calculated flight variables
    flightT = locCalcT(:, {'dive', 'time', 'vertSpeed', 'horzSpeed', 'speed', ...
        'speed_qc', 'glideAngle', 'buoyancy', 'north_displacement', 'east_displacement'});
    % write to CSV in repo
    writetable(flightT, fullfile(path_out, [glider '_20260128_flight_timeseries_modeled.csv']))

    % then just the engineering table as is
    writetable(engT, fullfile(path_out, [glider '_20260128_flight_timeseries_engineering.csv']))

end




