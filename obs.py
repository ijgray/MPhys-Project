import numpy as np
import xarray as xr
import netCDF4
import datetime
import os


"""
 Function to add time dimension in datetime form to a DataArray for use with MODIS data
args: xr DataArray 
"""
def add_time(da):
    # print(da.encoding['source'],type(da.encoding['source']))
    da = da.expand_dims(time = [datetime.datetime.now()])
    print(da)
    return da

"""
Regional means function
args: 1 year of MODIS data as xr dataset, 1 year of CERES data as xr dataset
output: dictionary of 3 regional annual mean values of different variables
"""
def regional_means(dsm, dsc):

    reg_means = {'reff':[],'SW':[],'LW':[],'net':[],'CSSW':[],'CSLW':[],'CSnet':[]}
    reff = (dsm['Mean']).squeeze()
    SW = (dsc['toa_sw_all_mon']).squeeze()
    LW = (dsc['toa_lw_all_mon']).squeeze()
    net = (dsc['toa_net_all_mon']).squeeze()
    CSSW = (dsc['toa_sw_clr_t_mon']).squeeze()
    CSLW = (dsc['toa_lw_clr_t_mon']).squeeze()
    variables = {'reff':reff,'SW':SW,'LW':LW,'CSSW':CSSW,'CSLW':CSLW}
    
    # define 3 latitude regions
    regionDict = {'NHex': slice(30,90), 'trop': slice(-30,30), 'SHex': slice(-90,-30)}
    coords = list(regionDict.values())

    for k, v in variables.items():
        # create a list to hold regional means of each variable
        v_list = []

        # find mean of the variable for each region and add it to the list for that variable
        for region in coords:
            v_reg = v.sel(latitude = region)
            coslat = np.cos(np.deg2rad(v_reg.latitude))
            v_rmean = v_reg.weighted(coslat).mean(['latitude','longitude','time'])
            #breakpoint()
            v_list.append(float(v_rmean))

        # assign the list of means for the current variable to the item in reg_means dictionary with the same name
        reg_means[k] = v_list
    coslat = np.cos(np.deg2rad(net.latitude))
    net_glob_mean = net.weighted(coslat).mean(['latitude','longitude','time'])
    
    return reg_means, net_glob_mean

"""
Main section. First I define the years which I'd like data for, then open CERES data as this is just one large dataset rather than separate files for each month. For each year, I open the relevant MODIS files, reset latitude coords to match CERES (-90 to 90 degrees rather than 0 to 180) and add a time dimension with appropriate values. I then call regional_means function to produce a dictionary of means for year variable for each year.
"""
# define set of years
years = np.arange(2013,2018)

# open CERES data to slice by year in loop below
ceres = xr.open_dataset('CERES_EBAF_Ed4.1_Subset_201301-201712.nc')
# rename CERES coords to match MODIS
new_dims = {'lat':'latitude','lon':'longitude'}
ceres = ceres.rename(new_dims)

# create dictionaries for date arrays and MODIS, CERES datasets which can be added to iteratively
dates = dict()
dsm = dict()
dsc = dict()
final_obs = dict()

reffNHex = []
refftrop =[]
reffSHex =[]
SWNHex=[]
SWtrop=[]
SWSHex=[]
LWNHex=[]
LWtrop=[]
LWSHex=[]
CSSWNHex=[]
CSSWtrop=[]
CSSWSHex=[]
CSLWNHex=[]
CSLWtrop=[]
CSLWSHex=[]
net = []

# loop over years, selecting and preparing relevant MODIS and CERES datasets to pass to regional_means
for year in years:
    dates[year] = xr.DataArray(np.arange(f"{year}-01", f"{year+1}-01", dtype="datetime64[M]"))
    print('hi')
    dsm[year] = xr.open_mfdataset(f'./CLDPROP_M3_MODIS_Aqua/CLDPROP_M3_MODIS_Aqua.A{year}*.nc', preprocess=add_time, concat_dim='time', group='Cloud_Effective_Radius_Liquid')
    
    dsm[year]['latitude'] = np.arange(-89.5,90.5)    # reset latitude dimension to match CERES

    dsm[year]['time'] = dates[year]                  # assign time values
    
    # CERES dataset 
    dsc[year] = ceres.sel(time = str(year))
    means, net_mean = regional_means(dsm[year], dsc[year])

    # add values to relevant lists
    reffNHex.append(means['reff'][0])
    refftrop.append(means['reff'][1])
    reffSHex.append(means['reff'][2])
    SWNHex.append(means['SW'][0])
    SWtrop.append(means['SW'][1])
    SWSHex.append(means['SW'][2])
    LWNHex.append(means['LW'][0])
    LWtrop.append(means['LW'][1])
    LWSHex.append(means['LW'][2])
    CSSWNHex.append(means['CSSW'][0])
    CSSWtrop.append(means['CSSW'][1])
    CSSWSHex.append(means['CSSW'][2])
    CSLWNHex.append(means['CSLW'][0])
    CSLWtrop.append(means['CSLW'][1])
    CSLWSHex.append(means['CSLW'][2])
    net.append(net_mean)

# add means to final_obs dictionary
final_obs['reffNHex'] = np.mean(reffNHex)
final_obs['refftrop'] = np.mean(refftrop)
final_obs['reffSHex'] = np.mean(reffSHex)
final_obs['SWNHex'] = np.mean(SWNHex)
final_obs['SWtrop'] = np.mean(SWtrop)
final_obs['SWSHex'] = np.mean(SWSHex)
final_obs['LWNHex'] = np.mean(LWNHex)
final_obs['LWtrop'] = np.mean(LWtrop)
final_obs['LWSHex'] = np.mean(LWSHex)
final_obs['CSSWNHex'] = np.mean(CSSWNHex)
final_obs['CSSWtrop'] = np.mean(CSSWtrop)
final_obs['CSSWSHex'] = np.mean(CSSWSHex)
final_obs['CSLWNHex'] = np.mean(CSLWNHex)
final_obs['CSLWtrop'] = np.mean(CSLWtrop)
final_obs['CSLWSHex'] = np.mean(CSLWSHex)
final_obs['net'] = np.mean(net)

print(final_obs)



