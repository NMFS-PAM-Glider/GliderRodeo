% workflow_rodeoPlanning


addpath(genpath('C:\Users\selene.fregosi\Documents\MATLAB\agate'))

% intialize with empty example config
CONFIG = agate;

kmlFile = 'A:\.shortcut-targets-by-id\1wy0sIBMKxaD-X5hgF3Ul7hJpsWjhgm9C\GliderRodeo\track planning - rodeo\rodeo_hourglass_v20260106.kml';

% make targets file
targetOut = makeTargetsFile(CONFIG, kmlFile, 'method', 'GR', 'radius', 1000);

% this created the targets file
degDecMin = [21 13.6076;	-158 10.2274; ...
    21 11.0925;	-158 19.3966; ...
    21 31.9611;	-158 18.3548; ...
    21 30.0704;	-158 25.1493; ...
    21 13.6076;	-158 10.2274];

% want to provide in dec deg too
degmin2decdeg(degDecMin);
% then pasted into a Google Sheet to share with group