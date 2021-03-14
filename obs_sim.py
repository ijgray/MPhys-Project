#!/bin/env python
"""
Compute simulated observables from UM. Observables are regional means for NH extratropical region (30 to 90 degrees latitude), tropical region (-30 to 30) and SH extratropical region (-90 to -30) of:

Liquid cloud effective radius (reff)
TOA SW, LW and net fluxes for all-sky and clear-sky conditions
"""

# useful imports
import json
import argparse
import os
import glob
import numpy as np
import xarray as xr
import datetime


"""
Regional means function for model data
args: 1 year of UM data as xr dataset
output: dictionary of 3 regional annual mean values of different variable
"""
def regional_means_model(ds):

    # create dictionary for desired regional means
    reg_means = dict()
    # define variables of interest and add to dictionary
    reff = (ds['UM_m01s01i245_vn405.0']/ds['UM_m01s01i246_vn405.0']).squeeze()
    SW = (ds['toa_outgoing_shortwave_flux']).squeeze()
    CSSW = (ds['toa_outgoing_shortwave_flux_assuming_clear_sky']).squeeze()
    LW = (ds['toa_outgoing_longwave_flux']).squeeze()
    CSLW = (ds['toa_outgoing_longwave_flux_assuming_clear_sky']).squeeze()
    inSW = (ds['toa_incoming_shortwave_flux']).squeeze()
    #net = inSW - SW - LW
    net = (ds['toa_incoming_shortwave_flux']-ds['toa_outgoing_shortwave_flux']-ds['toa_outgoing_longwave_flux']).squeeze()
    variables = {'reff':reff,'SW':SW,'LW':LW,'CSSW':CSSW,'CSLW':CSLW}

    # define 3 latitude regions to work with model coordinates
    regionDict = {'NHex':slice(90,30), 'trop':slice(30,-30), 'SHex':slice(-30,-90)}
    coords = list(regionDict.values())

    for k, v in variables.items():
        # create list to hold regional means of each variable
        v_list = []
        #find mean of the variable for each region and add it to the list for that variable
        for region in coords:
            v_reg = v.sel(latitude = region)
            coslat = np.cos(np.deg2rad(v_reg.latitude))
            v_rmean = v_reg.weighted(coslat).mean(['latitude','longitude','time'])
            v_list.append(float(v_rmean))

        #assign the list of means for the current variable to the item in reg_means dict with the same name
        reg_means[k] = v_list
    
    coslat = np.cos(np.deg2rad(net.latitude))
    net_glob_mean = net.weighted(coslat).mean(['latitude','longitude','time'])

    final_obs = dict()
    final_obs['reffNHex'] = reg_means['reff'][0]
    final_obs['refftrop'] = reg_means['reff'][1]
    final_obs['reffSHex'] = reg_means['reff'][2]
    final_obs['SWNHex'] = reg_means['SW'][0]
    final_obs['SWtrop'] = reg_means['SW'][1]
    final_obs['SWSHex'] = reg_means['SW'][2]
    final_obs['LWNHex'] = reg_means['LW'][0]
    final_obs['LWtrop'] = reg_means['LW'][1]
    final_obs['LWSHex'] = reg_means['LW'][2]
    final_obs['CSSWNHex'] = reg_means['CSSW'][0]
    final_obs['CSSWtrop'] = reg_means['CSSW'][1]
    final_obs['CSSWSHex'] = reg_means['CSSW'][2]
    final_obs['CSLWNHex'] = reg_means['CSLW'][0]
    final_obs['CSLWtrop'] = reg_means['CSLW'][1]
    final_obs['CSLWSHex'] = reg_means['CSLW'][2]
    final_obs['net'] = float(net_glob_mean)

    return final_obs



"""
Main model analysis section. Input file is model data
"""
# parse input arguments
parser = argparse.ArgumentParser(description='Post processing of UM data to provide simulated obs')

# add input and output files to parser
parser.add_argument('JSON_FILE', help='Name of JSON file')
parser.add_argument('-i', '--input',nargs='*', help='Name of input file')
parser.add_argument('OUTPUT', help='Name of output file')
parser.add_argument('-v', '--verbose', help='Provide verbose output', action='count', default=0)
#parse the args for use in fns
args = parser.parse_args()

json_file = args.JSON_FILE  # JSON to read
# ned to open file
with open(json_file,'r') as fp: 
# special python magic to deal with any file problems
    json_info = json.load(fp)  # read it


# work out files if needed, use input if given
if args.input is None:
    files = glob.glob(os.path.join('nc','apy','*.nc'))
    files5 = files[-5:]
else:
    files = args.input
    files5 = files[-5:]  # use only 5 years
    print(files)
try:
    options=json_info['postProcess'] # get the options
except KeyError:
    raise Exception("Need to provide post_process_options in "+args.JSON_FILE)
# note that options is not actually used..
# open model dataset
dsmodel = xr.open_mfdataset(files5)
# probably should be used here...
# find 5-year regional means of model variables
model_means = regional_means_model(dsmodel)

start_time = options.get('start_time','None')
end_time = options.get('end_time',None)
# verbose is an optional arg - if provided, assume user wants some helpful info
verbose = args.verbose
if verbose:
    print('start_time', start_time)
    print('end_time', end_time)
    if (verbose > 1):
        print('options are:', options)

output_file = args.OUTPUT
with open(output_file,'w') as fp:
    json.dump(model_means, fp)